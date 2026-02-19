This is a brilliant pivot. By invoking **Gunpei Yokoi’s "Lateral Thinking with Withered Technology"** (*Kareshi Gijutsu no Shisō*), we aren't trying to build a cutting-edge computer vision monster. Instead, we are using "withered" (mature, stable) tech like **mGBA’s Lua API** and **text-based memory scraping** to give a modern LLM "eyes" without the overhead of heavy video processing.

Here is a README designed to inspire and guide a Junior Developer to build this "Blue Ocean" autonomous player.

---

# Project: Lateral Red (LR-1)

### *An Autonomous Pokémon FireRed Agent via mGBA & LM Studio*

> "The Nintendo way of adapting technology is not to look for the state-of-the-art... but to utilize mature technology that can be mass-produced cheaply." — **Gunpei Yokoi**

## 🌊 The Philosophy

**Lateral Thinking with Withered Technology:** We do not need 40GB VRAM Vision Models to "see" the game. The game’s data already exists in RAM. We will use mature Lua scripting to "scrape" the game state into text, allowing even small, efficient LLMs to "read" the world and play it.

**Guiding Principles:**

1. **Do More with Less:** Prioritize text-based state over image-processing.
2. **The "Ghost in the Machine":** The LLM is both the player and the narrator.
3. **Sideways Thinking:** If the AI gets stuck in a corner, don't build a pathfinding algorithm—give the AI a "Compass" in its prompt.

---

## 🏗️ System Architecture

The project consists of three "mature" components working in a lateral loop:

1. **The Senses (mGBA + Lua):** A Lua script runs inside mGBA. It polls specific memory addresses (Player X/Y, Map ID, Menu Open, Dialogue Active) and writes them to a local `state.json`.
2. **The Brain (LM Studio):** A local LLM (Llama 3 or Mistral) running an OpenAI-compatible server. It receives the `state.json` and outputs a narrative + a command.
3. **The Nervous System (Python Bridge):** A lightweight Python script that:
* Reads the `state.json`.
* Formats the prompt for LM Studio.
* Sends the resulting command back to mGBA via the Lua socket/API.



---

## 🛠️ Junior Dev Implementation Roadmap

### Phase 1: The "Withered" State (Memory Scraping)

Instead of screenshots, your first task is to find a **Pokemon FireRed RAM Map**.

* **Goal:** Write a Lua script for mGBA that identifies:
* `0x02036E4C`: Player X-Coordinate
* `0x02036E4E`: Player Y-Coordinate
* `0x030030F0`: Current Map ID


* **Output:** A `current_context.txt` file that says: *"You are at (10,5) in Pallet Town. A person is standing in front of you."*

### Phase 2: The Command Bridge

mGBA's Lua API can inject inputs.

* **Goal:** Create a function `pressButton(button, frames)` that the Python bridge can trigger.
* **Blue Ocean Tip:** Don't just send one "Up" press. Create "Macros" like `Walk_North` (Hold Up for 16 frames).

### Phase 3: The Narrative Prompt

The prompt must force the LLM to think before it acts.

* **Format Requirement:**
> **Narrative:** "I've just received my Charmander! Now, I must head North to Viridian City to begin my journey."
> **Action:** `MOVE_NORTH`



---

## 🎯 The Win Condition

1. **Obtain 8 Badges.**
2. **Defeat the Elite Four.**
3. **Zero Human Intervention:** Once the script starts, the human only watches and listens to the narration.

---

## 🚀 Getting Started

1. **Install mGBA** (Development Build recommended for better Lua support).
2. **Setup LM Studio** with a local server on Port 1234.
3. **Run `bridge.py**` to start the loop.

---

### **Next Step for You**

