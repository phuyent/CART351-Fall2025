 CART 351 - Project I: Creative Coding in the Terminal

 🎮 Air Quality Quest: Montreal's Breathing Challenge

 Student: Huyen Tran Pham
 Project: Terminal-Based Interactive Game

---

 📖 Project Description

Air Quality Quest is an interactive terminal-based adventure game that combines real-time environmental data with engaging gameplay. Players explore Montreal's neighborhoods, visiting air quality monitoring stations while managing their health based on pollution exposure.

 Concept & Motivation

The inspiration for this project comes from:
- Environmental Awareness: Making air quality data accessible and engaging
- Gamification: Turning dry environmental data into an interactive experience
- Education: Teaching players about AQI scales and pollution impacts
- Local Focus: Using Montreal-specific data to create personal connection

The game transforms the abstract concept of air pollution into tangible consequences through health mechanics, encouraging players to seek out clean air spots while avoiding heavily polluted areas.

---

 🎯 Game Mechanics

 Core Gameplay Loop

1. Explore - Choose stations to visit (random or specific)
2. Discover - Learn real-time air quality data
3. Survive - Manage health based on pollution exposure
4. Score - Earn points for exploration and clean air discovery

 Health System

Your health is affected by air quality:

python
AQI 0-50:    +5 health  (Clean air heals you!)
AQI 51-100:  -2 health  (Minor impact)
AQI 101-150: -5 health  (Noticeable effects)
AQI 151-200: -10 health (Unhealthy)
AQI 201+:    -15 health (Hazardous)


 Scoring System

- Visit any station: +5 points
- Visit clean air station (AQI ≤ 50): +10 points
- Clean Air Point: Awarded for each AQI ≤ 50 visit

 Win/Lose Conditions

Victory: Collect 10 Clean Air Points  
Game Over: Health reaches 0%

---

 🔧 Technical Implementation

 Technologies Used
- Python 3.8+
- `requests` library (API calls)
- `colorama` library (cross-platform colors)
- `pyfiglet` library (ASCII art titles)

 API Integration

Uses the World Air Quality Index API:

python
API_BASE_URL = "https://api.waqi.info"
API_TOKEN = "your_token_here"

 Endpoints used:
 1. Search: /search/?keyword=montreal
 2. Station details: /feed/@{station_uid}/


API Calls:
- `fetch_montreal_stations()`: Gets all Montreal monitoring stations
- `fetch_station_details(uid)`: Gets detailed pollutant data for specific station

Error Handling:
- Network timeouts (10 second limit)
- Invalid API responses
- Missing data handling
- Graceful degradation without optional libraries

 Visual Design

Color Coding (AQI-based):
python
0-50:    Green   (Good)
51-100:  Yellow  (Moderate)
101-150: Magenta (Unhealthy for Sensitive)
151-200: Red     (Unhealthy)
201+:    Bright Red (Hazardous)


ASCII Art Elements:
- Dynamic air quality visualizations
- Health bars with visual indicators
- Decorative borders and separators
- Emoji integration for visual appeal

Special Effects:
- Typewriter text printing (`slow_print()`)
- Screen clearing for clean transitions
- Progress indicators during API calls
- Animated selections

---

 🎨 Creative Output Features

 1. Dynamic ASCII Visualizations

Different pollution levels create unique visual scenes:

Clean Air (AQI ≤ 50):

    ☀️ 
 ☁️    ☁️
🌳 🏠 🌳


Moderate (AQI 51-100):

   ☁️☁️
 ☁️    ☁️
🌳 🏭 🌳


Hazardous (AQI 200+):

☠️💀☠️💀☠️
☁️☁️☁️☁️☁️☁️
🏭💨🏭💨🏭💨


 2. Interactive Health Bar


Health: [████████████████░░░░] 80%
        ↑ Filled (Green/Yellow/Red based on level)
                        ↑ Empty


 3. Station Information Display


─────────────────────────────────────────────────
📍 Montreal, Quebec

😊 Air Quality Index: 35
   Status: Good

🗺️  Location: 45.5088°N, -73.5878°W

💨 Pollutant Levels:
   PM2.5: 8
   O₃: 12
   NO₂: 15
─────────────────────────────────────────────────


 4. Statistical Displays

- Real-time health bars
- Score counters
- Achievement tracking
- Visit history

---

 🎯 Project Requirements Met

 ✅ Python Programming

Functions Used:
- 20+ custom functions
- API request handling
- Data processing and filtering
- Game state management
- Error handling with try/except

Data Structures:
- Lists (stations_visited, pollutant data)
- Dictionaries (station info, API responses)
- Global variables (game state)

Control Flow:
- While loops (game loop)
- For loops (station iteration)
- If/elif/else (game logic)
- Function recursion (menu system)

 ✅ Air Quality API Integration

Live API Calls:
- Fetch Montreal stations on game start
- Request detailed data for each visit
- Parse JSON responses
- Handle API errors gracefully

Data Extraction:
- AQI values
- Station names and locations
- Pollutant levels (PM2.5, O₃, NO₂, etc.)
- Geographic coordinates

 ✅ Interactive User Interface

Input Methods:
- Menu navigation (1-6 choices)
- Station selection (numeric input)
- Press ENTER to continue
- Keyboard interrupts (Ctrl+C handling)

Input Validation:
- Number range checking
- Invalid input handling
- Error messages with retry

 ✅ Creative Terminal Output

Visual Elements:
- ASCII art title screens
- Color-coded information
- Dynamic visualizations
- Emoji indicators
- Health bars and progress displays

Text Effects:
- Typewriter printing
- Screen clearing
- Separator lines
- Formatted tables

Libraries Used:
- `colorama`: Cross-platform ANSI colors
- `pyfiglet`: Large ASCII art fonts
- Graceful fallbacks if not installed

---

 🚀 Installation & Setup

 Prerequisites

bash
 Python 3.8 or higher
python --version

 Create virtual environment
conda create --name project1env python=3.13
conda activate project1env


 Required Installation

bash
 Install required library
pip install requests


 Optional Installation (Recommended)

bash
 For colors (cross-platform)
pip install colorama

 For fancy ASCII titles
pip install pyfiglet


 Running the Game

bash
 Navigate to project directory
cd project-one

 Run the game
python air_quality_adventure.py


---

 🎮 How to Play

 Starting the Game

1. Run the Python script
2. Read the welcome screen
3. Press ENTER to begin

 Game Menu Options

1. 🔍 Explore Random Station
- Randomly selects a station to visit
- Good for quick gameplay

2. 📋 List All Stations
- Shows all Montreal monitoring stations
- Displays AQI for each
- Shows which you've visited (✓)

3. 🎯 Visit Specific Station
- Choose exact station by number
- Strategic gameplay option

4. 📊 View Detailed Stats
- See all statistics
- Check achievements
- Review visit history

5. 💡 Get Air Quality Tips
- Learn about air pollution
- Understand AQI scale
- Educational information

6. 🚪 Quit Game
- End game session
- View final score

 Strategy Tips

1. Check All Stations First (Option 2)
   - See which have good AQI
   - Plan your route

2. Balance Risk vs. Reward
   - Polluted areas give points but hurt health
   - Clean areas heal you but are less exciting

3. Monitor Your Health
   - Keep above 40% for safety
   - Visit clean areas if low

4. Aim for Efficiency
   - Visit 10 clean stations for quick win
   - Or explore all 20+ stations for high score

---

 📊 Game Statistics Tracked

 Core Stats
- Health: 0-100%
- Score: Total points earned
- Clean Air Points: Number of clean stations found
- Stations Visited: Total unique stations

 Achievements

Clean Air Champion 🏆
- Collect 10+ Clean Air Points

Explorer 🗺️
- Visit 15+ different stations

Perfect Health 💪
- Maintain 100% health

High Scorer 🎯
- Earn 100+ points

---

 🎨 Design Decisions

 Why This Approach?

1. Game Format
- Makes environmental data engaging
- Creates emotional investment
- Encourages exploration

2. Health Mechanic
- Concrete consequence of pollution
- Creates tension and strategy
- Easy to understand

3. Real-Time Data
- Always current information
- Connects to real world
- Educational value

4. Montreal Focus
- Local relevance for students
- Familiar locations
- 20+ monitoring stations

 Visual Design Philosophy

Clarity over Complexity
- Clean layouts
- Clear color coding
- Consistent formatting

Accessibility
- Works without colors (fallback)
- Works without ASCII art (fallback)
- Clear text descriptions

Engagement
- Emoji for quick recognition
- Animation for interest
- Progress feedback

---

 🔍 Code Structure

 Main Components

1. Configuration (Lines 1-60)
- Imports
- API credentials
- Global variables

2. Utility Functions (Lines 61-150)
- Screen management
- Text effects
- Visual elements

3. API Functions (Lines 151-220)
- Data fetching
- Error handling
- Response parsing

4. Game Logic (Lines 221-350)
- Health calculations
- Score updates
- Statistics tracking

5. Menu System (Lines 351-580)
- User interface
- Navigation
- Input handling

6. Game State (Lines 581-680)
- Win/lose conditions
- End screens
- State management

7. Main Loop (Lines 681-710)
- Game initialization
- Main execution
- Exit handling

 Key Functions

python
 API Integration
fetch_montreal_stations()     Get all stations
fetch_station_details(uid)    Get specific data

 Game Logic
calculate_health_impact(aqi)  Determine health change
update_player_stats()          Apply changes
check_game_status()           Win/lose detection

 Display
display_station_info()        Show station data
create_health_bar()           Visual health
create_pollution_visual()     ASCII scenes

 Navigation
show_main_menu()              Main interface
explore_random_station()      Random visit
visit_specific_station()      Chosen visit


---

 🐛 Error Handling

 Network Issues
- 10-second timeout on API calls
- Graceful degradation with empty lists
- Clear error messages to user

 Invalid Input
- Number validation
- Range checking
- Retry prompts

 Missing Data
- Handles stations with no AQI
- Fallback for missing pollutants
- Safe dictionary access

 Library Dependencies
- Works without colorama (no colors)
- Works without pyfiglet (simple title)
- Never crashes from missing imports

---

 📸 Screenshots

1. Welcome Screen
   - ASCII art title
   - Instructions

2. Main Menu
   - Health bar
   - Score display
   - Menu options

3. Station List
   - All Montreal stations
   - AQI color coding
   - Visit markers

4. Station Visit
   - Station details
   - Pollutant data
   - ASCII visualization
   - Health change

5. Victory Screen
   - Win message
   - Final statistics

6. Game Over Screen
   - Health depleted message
   - Final score

---

 🎓 Learning Outcomes

 Python Skills Demonstrated

- API Integration: Real-time data fetching
- Data Processing: JSON parsing, filtering
- User Input: Validation, error handling
- Control Flow: Complex game loops
- Functions: Modular, reusable code
- Error Handling: Try/except, graceful failures

 Creative Elements

- ASCII Art: Dynamic visualizations
- Color Theory: Information hierarchy
- UX Design: Clear navigation
- Game Design: Balanced mechanics
- Storytelling: Engaging narrative

 Technical Challenges Overcome

1. Cross-platform Colors
   - Used colorama for Windows compatibility
   - Implemented fallbacks

2. API Rate Limiting
   - Efficient calls (only when needed)
   - Caching station list

3. Data Validation
   - Handled missing/invalid AQI values
   - Safe dictionary access

4. User Experience
   - Clear feedback
   - Intuitive navigation
   - Helpful error messages

---

 🔮 Future Enhancements

 Potential Features

Gameplay:
- Difficulty levels (easy/hard)
- Multiplayer mode (compete for scores)
- Daily challenges
- Power-ups (masks, filters)

Data:
- Historical data analysis
- Weather correlation
- Prediction mini-game
- More cities

Visual:
- More ASCII art scenes
- Weather animations
- Sound effects (with beeps)
- Progress bars

Technical:
- Save game progress
- Leaderboard system
- Config file for settings
- Database for history

---

 📚 References & Resources

 APIs
- World Air Quality Index: https://aqicn.org/api/
- API Documentation: https://aqicn.org/json-api/doc/

 Libraries
- Requests: https://requests.readthedocs.io/
- Colorama: https://pypi.org/project/colorama/
- PyFiglet: https://pypi.org/project/pyfiglet/

 Inspiration
- Text-based adventure games (Zork, Colossal Cave)
- Environmental awareness games
- Data visualization best practices

 Learning Resources
- Python Official Docs: https://docs.python.org/
- Real Python Tutorials: https://realpython.com/
- Air Quality Standards: https://www.airnow.gov/

---

 🎬 Conclusion

Air Quality Quest successfully transforms environmental data into an engaging interactive experience. By combining real-time API data with game mechanics, it creates an educational yet entertaining way to learn about air pollution in Montreal.

The project demonstrates proficiency in Python programming, API integration, user interface design, and creative problem-solving—all while maintaining accessibility and providing a polished user experience entirely within the terminal.

Final Thought:  
*"The best way to understand data is to play with it."*

---

