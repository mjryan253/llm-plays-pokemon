-- Lateral Red (LR-1) -- mGBA Game Agent
-- Reads Pokemon FireRed (US v1.0 / BPRE) RAM, writes state.json, reads command.json

---------------------------------------------------------------------------
-- Configuration
-- Data dir: read from lua/data_dir.txt (written by bridge) so we use the
-- same absolute path as the Python bridge. If not found, fall back to
-- relative "data" (requires starting mGBA from project root).
---------------------------------------------------------------------------
local DATA_DIR = "data"
do
  local f = io.open("lua/data_dir.txt", "r")
  if f then
    local line = f:read("*l")
    f:close()
    if line and line ~= "" then
      DATA_DIR = line:gsub("%s+$", ""):gsub("^%s+", "")
    end
  else
    console:warn("Could not read lua/data_dir.txt. Start mGBA from the project root (e.g. cd llm-plays-pokemon) so the bridge and game agent use the same data folder.")
  end
end
local STATE_FILE = DATA_DIR .. "/state.json"
local STATE_TMP  = DATA_DIR .. "/state.json.tmp"
local CMD_FILE   = DATA_DIR .. "/command.json"
local FRAME_POLL = 30  -- write state every N frames

---------------------------------------------------------------------------
-- Memory addresses (FireRed US v1.0)
---------------------------------------------------------------------------
local ADDR = {
    SAVEBLOCK1_PTR = 0x03005008,
    SAVEBLOCK2_PTR = 0x0300500C,

    MAP_BANK_FIXED   = 0x02031DBC,
    MAP_NUMBER_FIXED = 0x02031DBD,
    PLAYER_MOVING    = 0x0203707B,
    MOVEMENT_LOCKED  = 0x0203707E,

    TEXT_BUFFER       = 0x02021D18,
    TEXT_BUFFER_LEN   = 256,

    BATTLE_FLAGS      = 0x02022B4C,

    PARTY_BASE        = 0x02024284,
    PARTY_SIZE        = 100,
    PARTY_COUNT_MAX   = 6,

    ENEMY_BASE        = 0x0202402C,
}

---------------------------------------------------------------------------
-- Gen 3 character set (partial, English)
---------------------------------------------------------------------------
local CHARSET = {
    [0xBB]="A",[0xBC]="B",[0xBD]="C",[0xBE]="D",[0xBF]="E",
    [0xC0]="F",[0xC1]="G",[0xC2]="H",[0xC3]="I",[0xC4]="J",
    [0xC5]="K",[0xC6]="L",[0xC7]="M",[0xC8]="N",[0xC9]="O",
    [0xCA]="P",[0xCB]="Q",[0xCC]="R",[0xCD]="S",[0xCE]="T",
    [0xCF]="U",[0xD0]="V",[0xD1]="W",[0xD2]="X",[0xD3]="Y",
    [0xD4]="Z",[0xD5]="a",[0xD6]="b",[0xD7]="c",[0xD8]="d",
    [0xD9]="e",[0xDA]="f",[0xDB]="g",[0xDC]="h",[0xDD]="i",
    [0xDE]="j",[0xDF]="k",[0xE0]="l",[0xE1]="m",[0xE2]="n",
    [0xE3]="o",[0xE4]="p",[0xE5]="q",[0xE6]="r",[0xE7]="s",
    [0xE8]="t",[0xE9]="u",[0xEA]="v",[0xEB]="w",[0xEC]="x",
    [0xED]="y",[0xEE]="z",[0x00]=" ",[0xAB]="!",[0xAC]="?",
    [0xAD]=".",[0xB8]=",",[0xBA]="-",[0xB4]="'",[0xB1]='"',
    [0xA1]="0",[0xA2]="1",[0xA3]="2",[0xA4]="3",[0xA5]="4",
    [0xA6]="5",[0xA7]="6",[0xA8]="7",[0xA9]="8",[0xAA]="9",
}

---------------------------------------------------------------------------
-- Gen 3 substructure decryption
---------------------------------------------------------------------------
local SUBSTRUCTURE_ORDER = {
    [0]  = "GAEM", [1]  = "GAME", [2]  = "GEAM", [3]  = "GEMA",
    [4]  = "GMAE", [5]  = "GMEA", [6]  = "AGEM", [7]  = "AGME",
    [8]  = "AEGM", [9]  = "AEMG", [10] = "AMGE", [11] = "AMEG",
    [12] = "EGAM", [13] = "EGMA", [14] = "EAGM", [15] = "EAMG",
    [16] = "EMGA", [17] = "EMAG", [18] = "MGAE", [19] = "MGEA",
    [20] = "MAGE", [21] = "MAEG", [22] = "MEGA", [23] = "MEAG",
}

local function bxor32(a, b)
    if bit32 then return bit32.bxor(a, b) end
    -- fallback using mGBA's util if bit32 unavailable
    local r = 0
    local p = 1
    for _ = 1, 32 do
        local ab = a % 2
        local bb = b % 2
        if ab ~= bb then r = r + p end
        a = math.floor(a / 2)
        b = math.floor(b / 2)
        p = p * 2
    end
    return r
end

local function band32(a, mask)
    if bit32 then return bit32.band(a, mask) end
    local r = 0
    local p = 1
    for _ = 1, 32 do
        if a % 2 == 1 and mask % 2 == 1 then r = r + p end
        a = math.floor(a / 2)
        mask = math.floor(mask / 2)
        p = p * 2
    end
    return r
end

local function rshift32(a, n)
    if bit32 then return bit32.rshift(a, n) end
    return math.floor(a / (2 ^ n))
end

---------------------------------------------------------------------------
-- Helpers
---------------------------------------------------------------------------
local function decodeString(addr, maxLen)
    local chars = {}
    for i = 0, maxLen - 1 do
        local b = emu:read8(addr + i)
        if b == 0xFF then break end
        local c = CHARSET[b]
        if c then
            chars[#chars + 1] = c
        end
    end
    return table.concat(chars)
end

local function readTextBuffer()
    local first = emu:read8(ADDR.TEXT_BUFFER)
    if first == 0x00 or first == 0xFF then return "" end
    return decodeString(ADDR.TEXT_BUFFER, ADDR.TEXT_BUFFER_LEN)
end

local function readPokemon(base)
    local pv   = emu:read32(base + 0x00)
    local otid = emu:read32(base + 0x04)

    if pv == 0 and otid == 0 then return nil end

    local nickname = decodeString(base + 0x08, 10)

    -- Decrypt the 48-byte data section
    local key = bxor32(pv, otid)
    local words = {}
    for i = 0, 11 do
        words[i] = bxor32(emu:read32(base + 0x20 + i * 4), key)
    end

    local order = SUBSTRUCTURE_ORDER[pv % 24]

    -- Locate Growth ("G") substructure
    local g_idx = string.find(order, "G") - 1
    local g_off = g_idx * 3
    local species_id  = band32(words[g_off], 0xFFFF)
    local held_item   = rshift32(words[g_off], 16)

    -- Locate Attacks ("A") substructure
    local a_idx = string.find(order, "A") - 1
    local a_off = a_idx * 3

    local move1 = band32(words[a_off], 0xFFFF)
    local move2 = band32(rshift32(words[a_off], 16), 0xFFFF)
    local move3 = band32(words[a_off + 1], 0xFFFF)
    local move4 = band32(rshift32(words[a_off + 1], 16), 0xFFFF)

    local pp_word = words[a_off + 2]
    local pp1 = band32(pp_word, 0xFF)
    local pp2 = band32(rshift32(pp_word, 8), 0xFF)
    local pp3 = band32(rshift32(pp_word, 16), 0xFF)
    local pp4 = band32(rshift32(pp_word, 24), 0xFF)

    -- Unencrypted battle stats (party only, bytes 0x50-0x63)
    local status    = emu:read32(base + 0x50)
    local level     = emu:read8(base + 0x54)
    local hp        = emu:read16(base + 0x56)
    local max_hp    = emu:read16(base + 0x58)
    local attack    = emu:read16(base + 0x5A)
    local defense   = emu:read16(base + 0x5C)
    local speed     = emu:read16(base + 0x5E)
    local sp_attack = emu:read16(base + 0x60)
    local sp_defense= emu:read16(base + 0x62)

    return {
        species_id = species_id,
        nickname = nickname,
        level = level,
        hp = hp,
        max_hp = max_hp,
        attack = attack,
        defense = defense,
        speed = speed,
        sp_attack = sp_attack,
        sp_defense = sp_defense,
        status = status,
        moves = {move1, move2, move3, move4},
        pp = {pp1, pp2, pp3, pp4},
        held_item_id = held_item,
    }
end

local function readParty(base)
    local party = {}
    for i = 0, ADDR.PARTY_COUNT_MAX - 1 do
        local pkmn = readPokemon(base + i * ADDR.PARTY_SIZE)
        if pkmn and pkmn.species_id ~= 0 then
            party[#party + 1] = pkmn
        end
    end
    return party
end

---------------------------------------------------------------------------
-- JSON serialization (minimal, no dependencies)
---------------------------------------------------------------------------
local function escapeJsonStr(s)
    s = s:gsub('\\', '\\\\')
    s = s:gsub('"', '\\"')
    s = s:gsub('\n', '\\n')
    s = s:gsub('\r', '\\r')
    s = s:gsub('\t', '\\t')
    return s
end

local function toJson(val)
    local t = type(val)
    if t == "nil" then
        return "null"
    elseif t == "boolean" then
        return val and "true" or "false"
    elseif t == "number" then
        return tostring(val)
    elseif t == "string" then
        return '"' .. escapeJsonStr(val) .. '"'
    elseif t == "table" then
        -- detect array vs object: array if sequential integer keys from 1
        local isArray = true
        local n = #val
        if n == 0 then
            for _ in pairs(val) do
                isArray = false
                break
            end
            if isArray then return "[]" end
        else
            for k in pairs(val) do
                if type(k) ~= "number" or k < 1 or k > n or math.floor(k) ~= k then
                    isArray = false
                    break
                end
            end
        end

        local parts = {}
        if isArray then
            for i = 1, n do
                parts[#parts + 1] = toJson(val[i])
            end
            return "[" .. table.concat(parts, ",") .. "]"
        else
            for k, v in pairs(val) do
                parts[#parts + 1] = '"' .. escapeJsonStr(tostring(k)) .. '":' .. toJson(v)
            end
            return "{" .. table.concat(parts, ",") .. "}"
        end
    end
    return "null"
end

---------------------------------------------------------------------------
-- Simple JSON parser for command.json
---------------------------------------------------------------------------
local function parseJson(str)
    local pos = 1
    local function skipWhitespace()
        while pos <= #str and str:sub(pos, pos):match("%s") do pos = pos + 1 end
    end
    local function parseValue()
        skipWhitespace()
        local c = str:sub(pos, pos)
        if c == '"' then
            pos = pos + 1
            local start = pos
            while pos <= #str do
                local ch = str:sub(pos, pos)
                if ch == '\\' then
                    pos = pos + 2
                elseif ch == '"' then
                    local s = str:sub(start, pos - 1)
                    pos = pos + 1
                    return s
                else
                    pos = pos + 1
                end
            end
            return ""
        elseif c == '{' then
            pos = pos + 1
            local obj = {}
            skipWhitespace()
            if str:sub(pos, pos) == '}' then pos = pos + 1; return obj end
            while true do
                skipWhitespace()
                local key = parseValue()
                skipWhitespace()
                pos = pos + 1 -- skip ':'
                local val = parseValue()
                obj[key] = val
                skipWhitespace()
                if str:sub(pos, pos) == ',' then
                    pos = pos + 1
                else
                    break
                end
            end
            skipWhitespace()
            if str:sub(pos, pos) == '}' then pos = pos + 1 end
            return obj
        elseif c == '[' then
            pos = pos + 1
            local arr = {}
            skipWhitespace()
            if str:sub(pos, pos) == ']' then pos = pos + 1; return arr end
            while true do
                arr[#arr + 1] = parseValue()
                skipWhitespace()
                if str:sub(pos, pos) == ',' then
                    pos = pos + 1
                else
                    break
                end
            end
            skipWhitespace()
            if str:sub(pos, pos) == ']' then pos = pos + 1 end
            return arr
        elseif c == 't' then
            pos = pos + 4; return true
        elseif c == 'f' then
            pos = pos + 5; return false
        elseif c == 'n' then
            pos = pos + 4; return nil
        else
            local start = pos
            while pos <= #str and str:sub(pos, pos):match("[%d%.%-eE%+]") do
                pos = pos + 1
            end
            return tonumber(str:sub(start, pos - 1)) or 0
        end
    end
    return parseValue()
end

---------------------------------------------------------------------------
-- Game mode detection
---------------------------------------------------------------------------
local function detectGameMode()
    local battleFlags = emu:read32(ADDR.BATTLE_FLAGS)
    if battleFlags ~= 0 then
        return "battle"
    end

    local textByte = emu:read8(ADDR.TEXT_BUFFER)
    if textByte ~= 0x00 and textByte ~= 0xFF then
        return "dialog"
    end

    local moveLocked = emu:read8(ADDR.MOVEMENT_LOCKED)
    if moveLocked == 1 then
        return "menu"
    end

    return "overworld"
end

---------------------------------------------------------------------------
-- State collection
---------------------------------------------------------------------------
local function collectState()
    local sb1 = emu:read32(ADDR.SAVEBLOCK1_PTR)

    local player_x   = emu:read16(sb1 + 0x000)
    local player_y   = emu:read16(sb1 + 0x002)
    local map_number  = emu:read8(sb1 + 0x004)
    local map_bank    = emu:read8(sb1 + 0x005)

    local is_moving       = emu:read8(ADDR.PLAYER_MOVING) ~= 0
    local movement_locked = emu:read8(ADDR.MOVEMENT_LOCKED) ~= 0
    local text_on_screen  = readTextBuffer()
    local battle_type     = emu:read32(ADDR.BATTLE_FLAGS)
    local game_mode       = detectGameMode()

    local party = readParty(ADDR.PARTY_BASE)
    local enemy = {}
    if game_mode == "battle" then
        enemy = readParty(ADDR.ENEMY_BASE)
    end

    return {
        frame = emu:currentFrame(),
        game_mode = game_mode,
        player_x = player_x,
        player_y = player_y,
        map_bank = map_bank,
        map_number = map_number,
        is_moving = is_moving,
        movement_locked = movement_locked,
        text_on_screen = text_on_screen,
        battle_type = battle_type,
        party = party,
        enemy = enemy,
    }
end

---------------------------------------------------------------------------
-- File I/O
---------------------------------------------------------------------------
local function writeStateFile(state)
    local json = toJson(state)
    local f = io.open(STATE_TMP, "w")
    if f then
        f:write(json)
        f:close()
        os.rename(STATE_TMP, STATE_FILE)
    end
end

local function readCommandFile()
    local f = io.open(CMD_FILE, "r")
    if not f then return nil end
    local content = f:read("*all")
    f:close()
    os.remove(CMD_FILE)
    if not content or content == "" then return nil end
    local ok, data = pcall(parseJson, content)
    if ok and data then return data end
    return nil
end

---------------------------------------------------------------------------
-- Button execution state machine
---------------------------------------------------------------------------
local cmdSteps = nil
local cmdStepIdx = 0
local cmdFramesLeft = 0

local function startCommand(cmd)
    local steps = cmd.steps or cmd
    if type(steps) ~= "table" or #steps == 0 then return end
    cmdSteps = steps
    cmdStepIdx = 1
    local step = cmdSteps[cmdStepIdx]
    local keys = tonumber(step.keys) or 0
    cmdFramesLeft = tonumber(step.frames) or 8
    emu:setKeys(keys)
end

local function tickCommand()
    if not cmdSteps then return false end

    cmdFramesLeft = cmdFramesLeft - 1
    if cmdFramesLeft > 0 then
        local step = cmdSteps[cmdStepIdx]
        emu:setKeys(tonumber(step.keys) or 0)
        return true
    end

    -- Advance to next step
    cmdStepIdx = cmdStepIdx + 1
    if cmdStepIdx > #cmdSteps then
        emu:setKeys(0)
        cmdSteps = nil
        return false
    end

    local step = cmdSteps[cmdStepIdx]
    cmdFramesLeft = tonumber(step.frames) or 8
    emu:setKeys(tonumber(step.keys) or 0)
    return true
end

---------------------------------------------------------------------------
-- Main frame callback
---------------------------------------------------------------------------
local frameCounter = 0

local function onFrame()
    -- Always tick the command executor
    local executing = tickCommand()

    frameCounter = frameCounter + 1

    -- Only write state and check for new commands on the poll interval
    if frameCounter >= FRAME_POLL then
        frameCounter = 0

        -- Write current state
        local ok, err = pcall(function()
            local state = collectState()
            writeStateFile(state)
        end)
        if not ok then
            console:error("State write error: " .. tostring(err))
        end

        -- Check for new command (only if not currently executing one)
        if not executing then
            local ok2, err2 = pcall(function()
                local cmd = readCommandFile()
                if cmd then
                    startCommand(cmd)
                end
            end)
            if not ok2 then
                console:error("Command read error: " .. tostring(err2))
            end
        end
    end
end

---------------------------------------------------------------------------
-- Bootstrap
---------------------------------------------------------------------------
console:log("Lateral Red (LR-1) game agent loaded")
console:log("State file: " .. STATE_FILE)
console:log("Command file: " .. CMD_FILE)
console:log("Polling every " .. FRAME_POLL .. " frames")

callbacks:add("frame", onFrame)
