import requests
import math
from datetime import datetime, timedelta
import json

# Moon phase meanings dictionary
moon_phase_meanings = {
    'New Moon': 'A time for new beginnings and setting intentions.',
    'Waxing Crescent': 'A period of growth and new ideas.',
    'First Quarter': 'A time to take action and make decisions.',
    'Waxing Gibbous': 'A period of refinement and development.',
    'Full Moon': 'A time for completion and release.',
    'Waning Gibbous': 'A period of reflection and gratitude.',
    'Last Quarter': 'A time to let go and release the old.',
    'Waning Crescent': 'A period of rest and introspection.'
}

# Refined Vedic 28 lunar mansions with meanings
vedic_lunar_mansions = [
    {"name": "Ashvini", "meaning": "New beginnings, quick healing, speed, and vitality."},
    {"name": "Bharani", "meaning": "Bearing burdens, nurturing, and transformation."},
    {"name": "Krittika", "meaning": "Cutting away impurities, determination, and protection."},
    {"name": "Rohini", "meaning": "Growth, fertility, beauty, and sensuality."},
    {"name": "Mrigashira", "meaning": "Search for knowledge, curiosity, and exploration."},
    {"name": "Ardra", "meaning": "Emotional storms, renewal, and intense transformation."},
    {"name": "Punarvasu", "meaning": "Renewal, return of the light, and recovery."},
    {"name": "Pushya", "meaning": "Nourishment, blossoming, and spiritual growth."},
    {"name": "Ashlesha", "meaning": "Intensity, embracing challenges, and deep transformation."},
    {"name": "Magha", "meaning": "Greatness, power, and ancestral connection."},
    {"name": "Purva Phalguni", "meaning": "Creativity, enjoyment, and artistic expression."},
    {"name": "Uttara Phalguni", "meaning": "Noble actions, leadership, and honor."},
    {"name": "Hasta", "meaning": "Skills, craftsmanship, and dexterity."},
    {"name": "Chitra", "meaning": "Brightness, creativity, and multifaceted talents."},
    {"name": "Swati", "meaning": "Independence, adaptability, and flexibility."},
    {"name": "Vishakha", "meaning": "Goal-oriented, determined, and purposeful."},
    {"name": "Anuradha", "meaning": "Devotion, loyalty, and following one’s path."},
    {"name": "Jyeshtha", "meaning": "Authority, seniority, and responsibility."},
    {"name": "Mula", "meaning": "Foundations, roots, and deep introspection."},
    {"name": "Purva Ashadha", "meaning": "Early victory, invincibility, and strength."},
    {"name": "Uttara Ashadha", "meaning": "Complete victory, perseverance, and final success."},
    {"name": "Shravana", "meaning": "Listening, learning, and acquiring knowledge."},
    {"name": "Dhanishta", "meaning": "Wealth, prosperity, and musical talents."},
    {"name": "Shatabhisha", "meaning": "Healing, mysticism, and hidden knowledge."},
    {"name": "Purva Bhadrapada", "meaning": "Optimism, spiritual insight, and foresight."},
    {"name": "Uttara Bhadrapada", "meaning": "Serenity, spiritual depth, and inner peace."},
    {"name": "Revati", "meaning": "Nourishment, wealth, and protection."},
    {"name": "Abhijit", "meaning": "Victory, subtlety, and divine favor."}
]

def fetch_ephemeris_data(body, date):
    cleaned_date = date.strip()
    start_time = cleaned_date + ' 00:00'
    stop_time = cleaned_date + ' 23:59'

    url = f"https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND='{body}'&EPHEM_TYPE='OBSERVER'&CENTER='500@399'&START_TIME='{start_time}'&STOP_TIME='{stop_time}'&STEP_SIZE='1 d'&QUANTITIES='1,31'"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception('Error fetching data from API')

    return response.text

def parse_ephemeris_data(content):
    lines = content.split('\n')
    data = {}
    start_data = False

    for line in lines:
        if line.startswith('$$SOE'):
            start_data = True
            continue
        if line.startswith('$$EOE'):
            break
        if start_data:
            fields = line.strip().split()
            if len(fields) >= 8:
                data['ra'] = float(fields[2])
                data['dec'] = float(fields[3])
                data['elong'] = float(fields[4])
    return data

def calculate_moon_phase(moon_data, sun_data):
    phase_angle = math.acos(math.cos(math.radians(moon_data['ra'] - sun_data['ra'])) * math.cos(math.radians(moon_data['dec'] - sun_data['dec'])))
    illuminated_fraction = (1 + math.cos(phase_angle)) / 2

    if illuminated_fraction < 0.1:
        phase = 'New Moon'
    elif illuminated_fraction < 0.25:
        phase = 'Waxing Crescent'
    elif illuminated_fraction < 0.5:
        phase = 'First Quarter'
    elif illuminated_fraction < 0.75:
        phase = 'Waxing Gibbous'
    elif illuminated_fraction < 0.9:
        phase = 'Full Moon'
    else:
        phase = 'Waning Gibbous'

    return phase

def get_lunar_mansion(ecliptic_longitude):
    mansion_index = int(ecliptic_longitude // (360 / 28))
    return vedic_lunar_mansions[mansion_index]

def fetch_moon_phase(date):
    moon_data_raw = fetch_ephemeris_data('301', date)  # 301 is the ID for the Moon
    sun_data_raw = fetch_ephemeris_data('10', date)  # 10 is the ID for the Sun

    moon_data = parse_ephemeris_data(moon_data_raw)
    sun_data = parse_ephemeris_data(sun_data_raw)

    moon_phase = calculate_moon_phase(moon_data, sun_data)
    lunar_mansion = get_lunar_mansion(moon_data['elong'])

    return moon_phase, lunar_mansion

def main():
    today = datetime.utcnow().date()
    week_data = []

    for i in range(7):
        date = today + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        day_of_week = date.strftime("%A")
        try:
            phase, lunar_mansion = fetch_moon_phase(date_str)
            moon_phase_meaning = moon_phase_meanings[phase]
            lunar_mansion_name = lunar_mansion['name']
            lunar_mansion_meaning = lunar_mansion['meaning']
        except Exception as e:
            phase = f"Error fetching data: {e}"
            moon_phase_meaning = "N/A"
            lunar_mansion_name = "N/A"
            lunar_mansion_meaning = "N/A"
        week_data.append({
            "date": date_str,
            "day": day_of_week,
            "moon_phase": phase,
            "moon_phase_meaning": moon_phase_meaning,
            "lunar_mansion_name": lunar_mansion_name,
            "lunar_mansion_meaning": lunar_mansion_meaning
        })

    with open('moon_phases.json', 'w') as f:
        json.dump(week_data, f, indent=4)

    return week_data

if __name__ == "__main__":
    weekly_data = main()
    print(json.dumps(weekly_data, indent=4))
