import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime

class KundliCalculator:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="kundli_app")
        self.tf = TimezoneFinder()

    def geocode_place(self, place: str):
        location = self.geolocator.geocode(place)
        if not location:
            raise ValueError(f"Could not geocode place: {place}")
        lat, lon = location.latitude, location.longitude
        timezone_str = self.tf.timezone_at(lng=lon, lat=lat)
        if not timezone_str:
            raise ValueError(f"Could not find timezone for: {place}")
        return lat, lon, timezone_str

    def to_utc(self, dob: str, tob: str, timezone_str: str):
        birth_datetime = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M:%S")
        timezone = pytz.timezone(timezone_str)
        birth_datetime_local = timezone.localize(birth_datetime)
        birth_datetime_utc = birth_datetime_local.astimezone(pytz.utc)
        return birth_datetime_utc

    def calculate_julian_day(self, dt_utc: datetime):
        return swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
        )

    def calculate_kundli(self, dob: str, tob: str, place: str):
        lat, lon, timezone_str = self.geocode_place(place)
        dt_utc = self.to_utc(dob, tob, timezone_str)
        jd = self.calculate_julian_day(dt_utc)

        # Planetary positions
        planets = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN, swe.TRUE_NODE]
        positions = {}
        for planet in planets:
            pos = swe.calc_ut(jd, planet)[0]
            positions[swe.get_planet_name(planet)] = pos[0]  # Longitude
        # Ketu is always opposite Rahu
        rahu_long = positions.get('True Node', 0)
        positions['Ketu'] = (rahu_long + 180) % 360

        # Ascendant and houses
        houses, ascmc = swe.houses(jd, lat, lon, b'A')

        # Ayanamsha (Lahiri)
        ayanamsha = swe.get_ayanamsa(jd)

        # Moon sign (Rashi)
        moon_long = positions['Moon'] - ayanamsha
        if moon_long < 0:
            moon_long += 360
        rashis = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        moon_sign_index = int(moon_long // 30)
        moon_sign = rashis[moon_sign_index]

        # Nakshatra
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        nakshatra_index = int((moon_long % 360) // (360/27))
        nakshatra = nakshatras[nakshatra_index]
        # Charan (Pada)
        charan = int(((moon_long % (360/27)) / ((360/27)/4)) + 1)

        # Tithi
        sun_long = positions['Sun'] - ayanamsha
        if sun_long < 0:
            sun_long += 360
        tithi_num = int(((moon_long - sun_long) % 360) / 12) + 1
        tithis = [
            "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
        ]
        tithi = tithis[(tithi_num-1)%15]
        paksha = "Shukla" if tithi_num <= 15 else "Krishna"

        # Yoga
        yoga_num = int(((moon_long + sun_long) % 360) / (360/27)) + 1
        yogas = [
            "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarman", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
        ]
        yoga = yogas[(yoga_num-1)%27]

        # Karana
        karana_num = int((((moon_long - sun_long) % 360) % 12) / 6) + 1
        karanas = [
            "Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kimstughna"
        ]
        karana = karanas[(karana_num-1)%11]

        # Sunrise and Sunset
        # geopos = [longitude, latitude, altitude]
        geopos = [lon, lat, 0]
        try:
            rsun = swe.rise_trans(jd, swe.SUN, None, swe.FLG_SWIEPH, 1 | 4, geopos, 0, 0)
            sunrise = swe.revjul(rsun[1][0]) if rsun[1][0] > 0 else None
            sunset = swe.revjul(rsun[1][1]) if rsun[1][1] > 0 else None
        except Exception:
            sunrise = sunset = None
        sunrise_str = None
        sunset_str = None
        if sunrise:
            sunrise_hour = int(float(sunrise[3]))
            sunrise_min = int(float(sunrise[4]))
            sunrise_sec = int(float(sunrise[5]))
            sunrise_str = f"{sunrise_hour:02d}:{sunrise_min:02d}:{sunrise_sec:02d}"
        if sunset:
            sunset_hour = int(float(sunset[3]))
            sunset_min = int(float(sunset[4]))
            sunset_sec = int(float(sunset[5]))
            sunset_str = f"{sunset_hour:02d}:{sunset_min:02d}:{sunset_sec:02d}"

        # Ayanamsha value
        ayanamsha_val = swe.get_ayanamsa(jd)

        # Utility functions for sign, house, nakshatra, pada, dignity, retrograde, combustion
        rashis = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        rashi_lords = [
            "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
        ]
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        exaltation = {
            "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"
        }
        debilitation = {
            "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"
        }
        moolatrikona = {
            "Sun": "Leo", "Moon": "Taurus", "Mars": "Aries", "Mercury": "Virgo", "Jupiter": "Sagittarius", "Venus": "Libra", "Saturn": "Aquarius"
        }
        # Helper for sign index
        def get_sign(lon):
            idx = int((lon % 360) // 30)
            return rashis[idx], idx
        # Helper for house index
        def get_house(lon, house_cusps):
            diff = [(lon - c) % 360 for c in house_cusps]
            min_diff = min(diff)
            idx = diff.index(min_diff)
            return idx+1
        # Helper for nakshatra and pada
        def get_nakshatra_pada(lon):
            nak_idx = int((lon % 360) // (360/27))
            pada = int(((lon % (360/27)) / ((360/27)/4)) + 1)
            return nakshatras[nak_idx], pada
        # Helper for dignity
        def get_dignity(planet, sign):
            if planet in exaltation and sign == exaltation[planet]:
                return "Exalted"
            if planet in debilitation and sign == debilitation[planet]:
                return "Debilitated"
            if planet in moolatrikona and sign == moolatrikona[planet]:
                return "Moolatrikona"
            if planet in rashi_lords and sign == planet:
                return "Own Sign"
            return "Neutral"
        # Helper for retrograde
        def is_retrograde(planet, jd):
            if planet in [swe.SUN, swe.MOON]:
                return False
            result = swe.calc_ut(jd, planet)[0]
            # result[3] is speed_longitude
            return result[3] < 0
        # Helper for combustion (approximate: Venus/Mercury/Mars/Jupiter/Saturn within 8 deg of Sun)
        def is_combust(planet, planet_lon, sun_lon):
            if planet not in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                return False
            diff = abs((planet_lon - sun_lon + 180) % 360 - 180)
            return diff < 8

        # Ascendant sign
        asc_sign, _ = get_sign(ascmc[0])
        # House cusp signs and lords
        house_list = []
        for i in range(12):
            sign, sign_idx = get_sign(houses[i])
            lord = rashi_lords[sign_idx]
            house_list.append({
                "number": i+1,
                "cusp_degree": houses[i],
                "sign": sign,
                "lord": lord
            })
        # Planets details
        sun_lon = positions["Sun"]
        planet_list = []
        for planet in positions.keys():
            lon = positions[planet]
            sign, sign_idx = get_sign(lon)
            house = get_house(lon, houses)
            deg_in_sign = lon % 30
            nak, pada = get_nakshatra_pada(lon)
            dignity = get_dignity(planet, sign)
            retro = False
            combust = False
            if planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
                swe_planet = getattr(swe, planet.upper()) if hasattr(swe, planet.upper()) else None
                if swe_planet is not None:
                    retro = is_retrograde(swe_planet, jd)
            combust = is_combust(planet, lon, sun_lon)
            planet_list.append({
                "name": planet,
                "longitude": lon,
                "sign": sign,
                "house": house,
                "degree_in_sign": deg_in_sign,
                "nakshatra": nak,
                "pada": pada,
                "dignity": dignity,
                "retrograde": retro,
                "combust": combust
            })
        # Aspects (basic Vedic aspects)
        aspect_list = []
        conjunctions = []
        for i, p1 in enumerate(planet_list):
            for j, p2 in enumerate(planet_list):
                if i >= j:
                    continue
                # Conjunction (within 8 degrees in same sign)
                if p1["sign"] == p2["sign"] and abs(p1["degree_in_sign"] - p2["degree_in_sign"]) < 8:
                    conjunctions.append({"planets": [p1["name"], p2["name"]], "sign": p1["sign"]})
                # 7th house aspect (opposition)
                diff = abs((p1["longitude"] - p2["longitude"] + 180) % 360 - 180)
                if abs(diff - 180) < 2:
                    aspect_list.append({"from": p1["name"], "to": p2["name"], "type": "Opposition (7th aspect)"})
                # Mars aspects 4th, 7th, 8th
                if p1["name"] == "Mars":
                    for aspect in [90, 180, 210]:
                        if abs(diff - aspect) < 2:
                            aspect_list.append({"from": p1["name"], "to": p2["name"], "type": f"Mars {aspect}° aspect"})
                # Jupiter aspects 5th, 7th, 9th
                if p1["name"] == "Jupiter":
                    for aspect in [150, 180, 210]:
                        if abs(diff - aspect) < 2:
                            aspect_list.append({"from": p1["name"], "to": p2["name"], "type": f"Jupiter {aspect}° aspect"})
                # Saturn aspects 3rd, 7th, 10th
                if p1["name"] == "Saturn":
                    for aspect in [90, 180, 270]:
                        if abs(diff - aspect) < 2:
                            aspect_list.append({"from": p1["name"], "to": p2["name"], "type": f"Saturn {aspect}° aspect"})
        kundli = {
            # I. Foundational Birth Data
            "input": {
                "dob": dob,
                "tob": tob,
                "place": place,
                "latitude": lat,
                "longitude": lon,
                "timezone": timezone_str
            },
            # II. Derived Astrological Details
            "ascendant": {
                "sign": asc_sign,
                "degree": ascmc[0]
            },
            "houses": house_list,
            "planets": planet_list,
            "ayanamsha": ayanamsha_val,
            "moon_sign": moon_sign,
            "nakshatra": nakshatra,
            "charan": charan,
            "tithi": {"paksha": paksha, "tithi": tithi, "number": tithi_num},
            "yoga": yoga,
            "karana": karana,
            "sunrise": sunrise_str,
            "sunset": sunset_str,
            # Planetary Relationships & Aspects
            "aspects": aspect_list,
            "conjunctions": conjunctions,
            # Yogas (advanced, not implemented)
            "yogas": [],
            # Divisional Charts (advanced, not implemented)
            "divisional_charts": {},
            # III. Dynamic Timing Factors (advanced, not implemented)
            "dasha": {},
            "transits": [],
        }
        return kundli
