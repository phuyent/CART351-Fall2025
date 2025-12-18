#!/usr/bin/env python3

# CART 351 - PROJECT I: CREATIVE CODING IN THE TERMINAL
# ======================================================
# Title: "Air Quality Quest: Montreal's Breathing Challenge"

# A terminal-based adventure game where you explore Montreal's neighborhoods,
# checking air quality at different stations. Your goal is to find the cleanest
# air spots while avoiding heavily polluted areas.

# Student: Huyen Tran Pham



import requests
import time
import sys
from datetime import datetime
import random

# Try to import colorama for cross-platform color support
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    # Fallback: no colors
    class Fore:
        RED = YELLOW = GREEN = CYAN = MAGENTA = BLUE = WHITE = RESET = ""
    class Back:
        BLACK = RED = GREEN = BLUE = RESET = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""

# Try to import pyfiglet for ASCII art
try:
    from pyfiglet import Figlet
    HAS_PYFIGLET = True
except ImportError:
    HAS_PYFIGLET = False


# ============================================
# GLOBAL VARIABLES & CONFIGURATION
# ============================================

API_TOKEN = "d398089c6ba7f09de5586cfee0a1d258e8ec741a"
API_BASE_URL = "https://api.waqi.info"

# Player stats
player_health = 100
player_score = 0
stations_visited = []
clean_air_points = 0

# Game state
current_location = None
game_running = True


# ============================================
# UTILITY FUNCTIONS
# ============================================

def clear_screen():
    #Clear the terminal screen
    print("\033[H\033[J", end="")


def slow_print(text, delay=0.03):
    #Print text with typewriter effect
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def print_separator(char="=", length=60):
    # Print a decorative separator line
    print(Fore.CYAN + char * length + Style.RESET_ALL)


def create_ascii_title():
    #Create fancy ASCII art title
    if HAS_PYFIGLET:
        f = Figlet(font='slant')
        title = f.renderText('Air Quest')
        print(Fore.CYAN + title + Style.RESET_ALL)
    else:
        # Fallback ASCII art
        print(Fore.CYAN + """
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║           🌬️  AIR QUALITY QUEST  🌬️              ║
    ║         Montreal's Breathing Challenge           ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
        """ + Style.RESET_ALL)


def create_health_bar(health):
    #Create visual health bar
    bar_length = 20
    filled = int((health / 100) * bar_length)
    empty = bar_length - filled
    
    if health > 70:
        color = Fore.GREEN
    elif health > 40:
        color = Fore.YELLOW
    else:
        color = Fore.RED
    
    bar = color + "█" * filled + Fore.WHITE + "░" * empty + Style.RESET_ALL
    return f"Health: [{bar}] {health}%"


def get_aqi_color_and_status(aqi):
    #Get color and status message based on AQI value
    try:
        aqi_value = int(aqi)
    except (ValueError, TypeError):
        return Fore.WHITE, "Unknown", "⚠️"
    
    if aqi_value <= 50:
        return Fore.GREEN, "Good", "😊"
    elif aqi_value <= 100:
        return Fore.YELLOW, "Moderate", "😐"
    elif aqi_value <= 150:
        return Fore.MAGENTA, "Unhealthy for Sensitive", "😷"
    elif aqi_value <= 200:
        return Fore.RED, "Unhealthy", "☣️"
    elif aqi_value <= 300:
        return Fore.RED + Style.BRIGHT, "Very Unhealthy", "💀"
    else:
        return Fore.RED + Style.BRIGHT, "Hazardous", "☠️"


# ============================================
# API FUNCTIONS
# ============================================

def fetch_montreal_stations():
    #Fetch all air quality stations in Montreal
    print(Fore.CYAN + "\n🔍 Scanning Montreal for air quality stations..." + Style.RESET_ALL)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/search/",
            params={"token": API_TOKEN, "keyword": "montreal"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok" and data.get("data"):
                stations = data["data"]
                print(Fore.GREEN + f"✓ Found {len(stations)} monitoring stations!" + Style.RESET_ALL)
                time.sleep(0.5)
                return stations
            else:
                print(Fore.RED + "✗ No stations found." + Style.RESET_ALL)
                return []
        else:
            print(Fore.RED + f"✗ API Error: {response.status_code}" + Style.RESET_ALL)
            return []
    
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"✗ Network Error: {e}" + Style.RESET_ALL)
        return []


def fetch_station_details(station_uid):
    #Fetch detailed information for a specific station
    try:
        response = requests.get(
            f"{API_BASE_URL}/feed/@{station_uid}/",
            params={"token": API_TOKEN},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                return data.get("data")
        return None
    
    except requests.exceptions.RequestException:
        return None


# ============================================
# GAME LOGIC FUNCTIONS
# ============================================

def calculate_health_impact(aqi):
    #Calculate health impact based on AQI
    try:
        aqi_value = int(aqi)
    except (ValueError, TypeError):
        return 0
    
    if aqi_value <= 50:
        return 5  # Gain health in clean air
    elif aqi_value <= 100:
        return -2
    elif aqi_value <= 150:
        return -5
    elif aqi_value <= 200:
        return -10
    else:
        return -15


def update_player_stats(aqi, station_name):
    #Update player health and score based on station visit
    global player_health, player_score, clean_air_points
    
    health_change = calculate_health_impact(aqi)
    player_health += health_change
    
    # Keep health between 0 and 100
    player_health = max(0, min(100, player_health))
    
    # Award points
    if health_change > 0:
        points = 10
        clean_air_points += 1
        print(Fore.GREEN + f"\n✓ Clean air! +{points} points, +{health_change} health!" + Style.RESET_ALL)
    else:
        points = 5
        print(Fore.RED + f"\n✗ Polluted air! {health_change} health." + Style.RESET_ALL)
    
    player_score += points
    stations_visited.append(station_name)


def display_stats():
    #Display current player statistics
    print_separator()
    print(create_health_bar(player_health))
    print(Fore.CYAN + f"Score: {player_score} points" + Style.RESET_ALL)
    print(Fore.GREEN + f"Clean Air Points: {clean_air_points} 🌿" + Style.RESET_ALL)
    print(Fore.YELLOW + f"Stations Visited: {len(stations_visited)}" + Style.RESET_ALL)
    print_separator()


def display_station_info(station, details=None):
    #Display detailed station information with visual flair
    print_separator("─")
    
    # Station name
    station_name = station.get("station", {}).get("name", "Unknown Station")
    print(Fore.CYAN + Style.BRIGHT + f"\n📍 {station_name}" + Style.RESET_ALL)
    
    # AQI value
    aqi = station.get("aqi", "-")
    color, status, emoji = get_aqi_color_and_status(aqi)
    
    print(f"\n{emoji} Air Quality Index: " + color + Style.BRIGHT + f"{aqi}" + Style.RESET_ALL)
    print(f"   Status: " + color + f"{status}" + Style.RESET_ALL)
    
    # Location
    geo = station.get("station", {}).get("geo", [])
    if len(geo) == 2:
        print(Fore.WHITE + f"\n🗺️  Location: {geo[0]}°N, {geo[1]}°W" + Style.RESET_ALL)
    
    # Detailed pollutant data if available
    if details and "iaqi" in details:
        print(Fore.CYAN + "\n💨 Pollutant Levels:" + Style.RESET_ALL)
        iaqi = details["iaqi"]
        
        pollutants = {
            "pm25": "PM2.5",
            "pm10": "PM10",
            "o3": "Ozone",
            "no2": "NO₂",
            "so2": "SO₂",
            "co": "CO"
        }
        
        for key, name in pollutants.items():
            if key in iaqi:
                value = iaqi[key].get("v", "N/A")
                print(f"   {name}: {value}")
    
    print_separator("─")


def create_pollution_visual(aqi):
    #Create ASCII visual representation of pollution level
    try:
        aqi_value = int(aqi)
    except (ValueError, TypeError):
        return ""
    
    if aqi_value <= 50:
        # Clean air - sunshine
        return """
        ☀️ 
     ☁️    ☁️
   🌳 🏠 🌳
        """
    elif aqi_value <= 100:
        # Moderate - some clouds
        return """
       ☁️☁️
     ☁️    ☁️
   🌳 🏭 🌳
        """
    elif aqi_value <= 150:
        # Unhealthy - more smog
        return """
     ☁️☁️☁️☁️
    ☁️☁️☁️☁️☁️
   🏭💨🏭💨🏭
        """
    else:
        # Very unhealthy - heavy smog
        return """
    ☠️💀☠️💀☠️
   ☁️☁️☁️☁️☁️☁️
  🏭💨🏭💨🏭💨
        """


# ============================================
# GAME MENU & NAVIGATION
# ============================================

def show_welcome_screen():
    #Display welcome screen with game instructions
    clear_screen()
    create_ascii_title()
    
    print(Fore.YELLOW + """
    Welcome, Air Quality Explorer!
    
    Your mission: Navigate Montreal's neighborhoods to find the
    cleanest air while surviving the pollution. 
    
    🎯 OBJECTIVES:
    • Visit air quality monitoring stations
    • Find clean air spots (+health, +points)
    • Avoid heavily polluted areas (-health)
    • Collect 10 Clean Air Points to win!
    
    ⚠️  WARNING: Your health decreases in polluted areas.
                If it reaches 0, game over!
    
    """ + Style.RESET_ALL)
    
    input(Fore.GREEN + "Press ENTER to begin your quest..." + Style.RESET_ALL)


def show_main_menu(stations):
    #Display main game menu
    while game_running and player_health > 0:
        clear_screen()
        create_ascii_title()
        display_stats()
        
        print(Fore.YELLOW + "\n🗺️  CHOOSE YOUR NEXT MOVE:\n" + Style.RESET_ALL)
        print("1. 🔍 Explore Random Station")
        print("2. 📋 List All Stations")
        print("3. 🎯 Visit Specific Station")
        print("4. 📊 View Detailed Stats")
        print("5. 💡 Get Air Quality Tips")
        print("6. 🚪 Quit Game")
        
        choice = input(Fore.CYAN + "\nEnter your choice (1-6): " + Style.RESET_ALL).strip()
        
        if choice == "1":
            explore_random_station(stations)
        elif choice == "2":
            list_all_stations(stations)
        elif choice == "3":
            visit_specific_station(stations)
        elif choice == "4":
            show_detailed_stats()
        elif choice == "5":
            show_air_quality_tips()
        elif choice == "6":
            quit_game()
            break
        else:
            print(Fore.RED + "\n⚠️  Invalid choice. Try again." + Style.RESET_ALL)
            time.sleep(1)
        
        # Check win/lose conditions
        check_game_status()


def explore_random_station(stations):
    #Randomly select and visit a station
    if not stations:
        print(Fore.RED + "\n⚠️  No stations available!" + Style.RESET_ALL)
        input("\nPress ENTER to continue...")
        return
    
    clear_screen()
    print(Fore.CYAN + "\n🎲 Randomly selecting a station..." + Style.RESET_ALL)
    time.sleep(1)
    
    station = random.choice(stations)
    visit_station(station)


def list_all_stations(stations):
    #Display list of all available stations
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + "\n📋 ALL MONTREAL AIR QUALITY STATIONS\n" + Style.RESET_ALL)
    
    for i, station in enumerate(stations, 1):
        name = station.get("station", {}).get("name", "Unknown")
        aqi = station.get("aqi", "-")
        color, status, emoji = get_aqi_color_and_status(aqi)
        
        visited = "✓" if name in stations_visited else " "
        print(f"{visited} {i:2d}. {name:40s} {emoji} AQI: " + color + f"{aqi}" + Style.RESET_ALL)
    
    input(Fore.GREEN + "\nPress ENTER to return to menu..." + Style.RESET_ALL)


def visit_specific_station(stations):
    #Allow player to choose a specific station to visit
    clear_screen()
    print(Fore.CYAN + "\n📍 SELECT A STATION TO VISIT\n" + Style.RESET_ALL)
    
    for i, station in enumerate(stations, 1):
        name = station.get("station", {}).get("name", "Unknown")
        aqi = station.get("aqi", "-")
        visited = "✓" if name in stations_visited else " "
        print(f"{visited} {i:2d}. {name}")
    
    try:
        choice = input(Fore.CYAN + "\nEnter station number (or 0 to cancel): " + Style.RESET_ALL)
        choice_num = int(choice)
        
        if choice_num == 0:
            return
        
        if 1 <= choice_num <= len(stations):
            station = stations[choice_num - 1]
            visit_station(station)
        else:
            print(Fore.RED + "\n⚠️  Invalid station number!" + Style.RESET_ALL)
            time.sleep(1)
    except ValueError:
        print(Fore.RED + "\n⚠️  Please enter a valid number!" + Style.RESET_ALL)
        time.sleep(1)


def visit_station(station):
    #Visit a station and display full information
    clear_screen()
    
    station_name = station.get("station", {}).get("name", "Unknown")
    uid = station.get("uid")
    
    print(Fore.CYAN + f"\n🚶 Traveling to {station_name}..." + Style.RESET_ALL)
    time.sleep(1)
    
    # Fetch detailed data
    details = fetch_station_details(uid) if uid else None
    
    # Display station info
    display_station_info(station, details)
    
    # Show pollution visual
    aqi = station.get("aqi", "-")
    print(create_pollution_visual(aqi))
    
    # Update player stats
    try:
        aqi_value = int(aqi)
        update_player_stats(aqi_value, station_name)
    except (ValueError, TypeError):
        print(Fore.YELLOW + "\n⚠️  Unable to determine air quality impact." + Style.RESET_ALL)
    
    # Show updated stats
    print()
    display_stats()
    
    input(Fore.GREEN + "\nPress ENTER to continue..." + Style.RESET_ALL)


def show_detailed_stats():
    #Show detailed game statistics
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + "\n📊 DETAILED STATISTICS\n" + Style.RESET_ALL)
    
    display_stats()
    
    print(Fore.YELLOW + "\n🏆 Achievements:" + Style.RESET_ALL)
    
    if clean_air_points >= 10:
        print(Fore.GREEN + "   ✓ Clean Air Champion! (10+ clean stations)" + Style.RESET_ALL)
    if len(stations_visited) >= 15:
        print(Fore.GREEN + "   ✓ Explorer! (15+ stations visited)" + Style.RESET_ALL)
    if player_health == 100:
        print(Fore.GREEN + "   ✓ Perfect Health!" + Style.RESET_ALL)
    if player_score >= 100:
        print(Fore.GREEN + "   ✓ High Scorer! (100+ points)" + Style.RESET_ALL)
    
    print(Fore.CYAN + "\n📝 Stations Visited:" + Style.RESET_ALL)
    for i, name in enumerate(stations_visited, 1):
        print(f"   {i}. {name}")
    
    input(Fore.GREEN + "\nPress ENTER to return to menu..." + Style.RESET_ALL)


def show_air_quality_tips():
    #Display educational air quality information
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + "\n💡 AIR QUALITY TIPS & INFO\n" + Style.RESET_ALL)
    
    tips = [
        ("🌳", "Green spaces naturally filter air pollution"),
        ("🚴", "Cycling and walking reduce vehicle emissions"),
        ("🏭", "Industrial areas typically have higher pollution"),
        ("🌬️", "Wind helps disperse pollutants"),
        ("☀️", "Sunny days can increase ozone levels"),
        ("😷", "Wear masks in heavily polluted areas"),
        ("🏠", "Indoor plants can improve air quality"),
        ("⏰", "Air quality often better in mornings"),
    ]
    
    print(Fore.YELLOW + "DID YOU KNOW?\n" + Style.RESET_ALL)
    for emoji, tip in tips:
        print(f"{emoji}  {tip}")
    
    print(Fore.CYAN + "\n📖 AQI SCALE REFERENCE:" + Style.RESET_ALL)
    print(Fore.GREEN + "   0-50:   Good" + Style.RESET_ALL)
    print(Fore.YELLOW + "   51-100: Moderate" + Style.RESET_ALL)
    print(Fore.MAGENTA + "   101-150: Unhealthy for Sensitive Groups" + Style.RESET_ALL)
    print(Fore.RED + "   151-200: Unhealthy" + Style.RESET_ALL)
    print(Fore.RED + Style.BRIGHT + "   201+:   Very Unhealthy/Hazardous" + Style.RESET_ALL)
    
    input(Fore.GREEN + "\nPress ENTER to return to menu..." + Style.RESET_ALL)


# ============================================
# GAME STATE MANAGEMENT
# ============================================

def check_game_status():
    #Check if player has won or lost
    global game_running
    
    if player_health <= 0:
        show_game_over()
        game_running = False
    elif clean_air_points >= 10:
        show_victory()
        game_running = False


def show_game_over():
    #Display game over screen
    clear_screen()
    
    print(Fore.RED + Style.BRIGHT + """
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║           GAME OVER!  💀              ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
    """ + Style.RESET_ALL)
    
    print(Fore.YELLOW + "\nYour health reached zero from pollution exposure." + Style.RESET_ALL)
    print(Fore.CYAN + f"\nFinal Score: {player_score} points" + Style.RESET_ALL)
    print(Fore.GREEN + f"Stations Visited: {len(stations_visited)}" + Style.RESET_ALL)
    print(Fore.GREEN + f"Clean Air Points: {clean_air_points}" + Style.RESET_ALL)
    
    input(Fore.GREEN + "\nPress ENTER to exit..." + Style.RESET_ALL)


def show_victory():
    #Display victory screen
    clear_screen()
    
    print(Fore.GREEN + Style.BRIGHT + """
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║         🎉 VICTORY! 🎉                ║
    ║    You're a Clean Air Champion!       ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
    """ + Style.RESET_ALL)
    
    print(Fore.YELLOW + "\nYou found 10 clean air spots in Montreal!" + Style.RESET_ALL)
    print(Fore.CYAN + f"\nFinal Score: {player_score} points" + Style.RESET_ALL)
    print(Fore.GREEN + f"Final Health: {player_health}%" + Style.RESET_ALL)
    print(Fore.GREEN + f"Stations Visited: {len(stations_visited)}" + Style.RESET_ALL)
    
    input(Fore.GREEN + "\nPress ENTER to exit..." + Style.RESET_ALL)


def quit_game():
    #Quit the game
    clear_screen()
    print(Fore.CYAN + "\n👋 Thanks for playing Air Quality Quest!" + Style.RESET_ALL)
    print(Fore.YELLOW + f"Final Score: {player_score} points" + Style.RESET_ALL)
    print(Fore.GREEN + f"Stations Visited: {len(stations_visited)}" + Style.RESET_ALL)
    time.sleep(2)


# ============================================
# MAIN GAME LOOP
# ============================================

def main():
    #Main game function
    global game_running
    
    # Show welcome screen
    show_welcome_screen()
    
    # Fetch stations
    stations = fetch_montreal_stations()
    
    if not stations:
        print(Fore.RED + "\n⚠️  Unable to fetch station data. Please check your internet connection." + Style.RESET_ALL)
        print(Fore.YELLOW + "     Make sure the API token is correct." + Style.RESET_ALL)
        return
    
    # Start game loop
    show_main_menu(stations)
    
    # Exit
    clear_screen()
    print(Fore.CYAN + "\n🌬️  Breathe clean, live well! 🌬️\n" + Style.RESET_ALL)


# ============================================
# ENTRY POINT
# ============================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n⚠️  Game interrupted. Goodbye!" + Style.RESET_ALL)
        sys.exit(0)
