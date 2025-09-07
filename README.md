# Moonlit

A Discord mini-game bot where players roleplay as witches, join covens, and grow their magical power together.  
Designed to be approachable for casual players but deep enough to keep engaged players busy with cooperative rituals, spellcrafting, and seasonal events.  

---

## ✨ Features

- **Daily Rituals** – Gather herbs, brew potions, and perform divinations.  
- **Familiars** – Adopt and interact with a magical animal companion.  
- **Coven System** – Join or create covens, collaborate on shared goals, and level up your sanctum.  
- **Chant Rituals** – Group activities where coven members recite magical chants in sequence.    
- **Seasonal Festivals** – Limited-time coven events aligned with moon phases and folklore holidays.  
- **Grimoire Collection** – Unlock lore, recipes, and familiars as you progress.  
- **Leaderboards & Titles** – Show off your progression with ranks and coven achievements.  

---

## 🏗️ Tech Overview

- **Language:** Python 3.13+  
- **Framework:** [discord.py](https://discordpy.readthedocs.io/)
- **Core Systems:**  
  - Slash command interface  
  - Event listener for ritual chants  
  - Game logic engine for rituals, crafting, and duels  
  - Database for persistent user/coven data  
- **External APIs:**  
  - Moon phase API to influence rituals and events  

---

## 🚀 Getting Started

See the Installation section below for setup instructions.

---

## 🛠️ Installation

### Using Docker (Recommended)

1. **Clone the repository:**
   ```sh
   git clone https://github.com/robbitsu/Moonlit
   cd Moonlit
   ```
2. **Build and start the services:**
   ```sh
   docker-compose up --build
   ```
   This will build and run both the API and Discord bot containers.

### Manual Setup

#### Prerequisites
- Python 3.13+
- (Recommended) [virtualenv](https://virtualenv.pypa.io/)

#### API Setup
1. Navigate to the API directory:
   ```sh
   cd api
   ```
2. (Optional) Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the API server:
   ```sh
   uvicorn src.api:app --reload --port 8123
   ```

#### Bot Setup
1. Navigate to the bot directory:
   ```sh
   cd bot
   ```
2. (Optional) Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```sh
   python src/bot.py
   ```

---

## 🗺️ Roadmap


---

## 📄 License

This project is licensed under the GNU Lesser General Public License v3.0. See the [LICENSE](./LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! To contribute:
- Fork the repository and create your branch from `main`.
- Ensure code follows project style and includes relevant documentation.
- Submit a pull request with a clear description of your changes.
- For major changes, please open an issue first to discuss what you would like to change.

---

## 🌌 Acknowledgements

This project draws on imagery and folklore inspired by witches, covens, and magical traditions in **fiction and fantasy**.  

We want to acknowledge and respect real-life pagan, Wiccan, and other spiritual paths.  
Moonlit is made in **good faith as a work of fantasy entertainment**, not as a representation or parody of real-world practices or beliefs.  

Inspired by cozy fantasy, folklore, and community-driven play.  
