"""
create_excel_data.py - Generates Roamora Travels Tour Packages Catalog (.xlsx)
for the RAG Chatbot Knowledge Base.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def create_travel_packages_excel(output_path="data/products.xlsx"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tour_Packages_Catalog"
    
    # Headers
    headers = [
        "Package Code",
        "Package Name",
        "Destination",
        "Country",
        "Duration",
        "Standard Price ($)",
        "Discounted Price ($)",
        "Availability & Group Size",
        "Included Services",
        "Excluded Services",
        "Key Highlights & Itinerary",
        "Customer Rating & Reviews"
    ]
    
    # Tour package rows for Roamora Travels
    packages = [
        [
            "ROAM-PK-01",
            "Hunza Adventure & Cultural Odyssey",
            "Hunza Valley & Karimabad",
            "Pakistan",
            "5 Days / 4 Nights",
            "$599",
            "$499",
            "Available Weekly (Min 2, Max 12 persons)",
            "4-star hotel stay with mountain views, chauffeured 4x4 Prado, professional local guide, breakfast & dinners, Attabad Lake boating passes, Altit & Baltit Fort entry fees.",
            "International flights, personal shopping, lunch meals, travel insurance.",
            "Scenic Karakoram Highway drive, sunrise over Rakaposhi (7,788m), exploration of ancient 800-year-old Baltit Fort, turquoise waters of Attabad Lake, Passu Cones suspension bridge walk.",
            "4.9 / 5.0 (340 reviews) - 'Life-changing mountain views and warm hospitality.'"
        ],
        [
            "ROAM-UAE-02",
            "Dubai Luxury Escape & Desert Safari",
            "Dubai City & Arabian Desert",
            "United Arab Emirates",
            "4 Days / 3 Nights",
            "$849",
            "$699",
            "Available Daily (Private or Small Group)",
            "5-star hotel in Downtown Dubai or Marina, private airport transfers, 4x4 desert dune bashing safari with BBQ dinner & show, Burj Khalifa 124th floor ticket, Dubai Marina yacht dinner cruise.",
            "UAE tourist visa fee, personal shopping, alcoholic beverages during desert safari.",
            "Spectacular views from Burj Khalifa, thrilling 4x4 desert safari with sandboarding and camel rides, luxury Marina yacht cruise at sunset, exploration of Old Dubai Gold & Spice Souks.",
            "4.8 / 5.0 (520 reviews) - 'Flawless luxury arrangements and hassle-free VIP transfers.'"
        ],
        [
            "ROAM-ID-03",
            "Bali Tropical Retreat & Island Wellness",
            "Ubud & Seminyak",
            "Indonesia",
            "6 Days / 5 Nights",
            "$950",
            "$799",
            "Available Year-Round (Solo, Couples, Families)",
            "Private villa with plunge pool in Ubud, beach resort in Seminyak, daily breakfast, private air-conditioned van & driver, sacred Tirta Empul temple tour, Uluwatu sunset fire dance tickets.",
            "International airfare, lunch/dinners not specified, personal spa treatments.",
            "Iconic Tegallalang rice terrace jungle swing, tranquil wellness spa sessions, sunset at Uluwatu Cliff Temple with Kecak dance, day excursion to Nusa Penida crystalline beaches.",
            "4.9 / 5.0 (410 reviews) - 'The perfect blend of relaxation, vibrant culture, and tropical nature.'"
        ],
        [
            "ROAM-PK-04",
            "Skardu Karakoram & Turquoise Lakes Expedition",
            "Skardu & Shigar Valley",
            "Pakistan",
            "6 Days / 5 Nights",
            "$749",
            "$649",
            "May through October (Small Group 4-10 persons)",
            "Stay at Shangrila Resort & Shigar Serena Fort, 4x4 mountain jeeps, daily breakfast & dinner, dedicated mountain guide, permits for Deosai Plains.",
            "Flights to/from Islamabad, high-altitude gear rental, tipping.",
            " Shangrila Lake (Lower Kachura), boat tour on Upper Kachura Lake, sunset over the Cold Desert of Katpana, Deosai National Park ('Land of Giants'), historic Shigar Fort heritage walk.",
            "4.9 / 5.0 (280 reviews) - 'Unreal landscapes, like stepping into another planet.'"
        ],
        [
            "ROAM-TR-05",
            "Istanbul Two Continents Heritage & Culinary Journey",
            "Istanbul (European & Asian sides)",
            "Türkiye",
            "5 Days / 4 Nights",
            "$720",
            "$599",
            "Available Weekly (Year-Round)",
            "Boutique hotel in Sultanahmet, private Bosphorus yacht sunset cruise, skip-the-line passes to Hagia Sophia, Topkapi Palace & Basilica Cistern, guided Grand Bazaar culinary walking tour.",
            "Turkish e-Visa, international airfare, optional Turkish bath (Hammam) session.",
            "Walking through 1,500 years of history at Hagia Sophia, tasting authentic kebabs and baklava in Kadıköy, sunset cruise across the continental divide between Europe and Asia.",
            "4.7 / 5.0 (310 reviews) - 'Knowledgeable guides and unforgettable food tastings.'"
        ],
        [
            "ROAM-FR-06",
            "Paris Romance, Art & Gastronomy",
            "Paris & Versailles",
            "France",
            "5 Days / 4 Nights",
            "$1,199",
            "$999",
            "Available Year-Round (Couples & Private Groups)",
            "4-star boutique hotel near Saint-Germain-des-Prés, Seine River champagne cruise, Eiffel Tower summit tickets, guided Louvre Museum tour, private day excursion to Palace of Versailles.",
            "Schengen visa fees, international flights, discretionary guide tips.",
            "Eiffel Tower panoramic summit visit, Mona Lisa VIP viewing, stroll through cobblestone streets of Montmartre, royal gardens and Hall of Mirrors at Versailles.",
            "4.8 / 5.0 (215 reviews) - 'Magical romantic getaway arranged to absolute perfection.'"
        ],
        [
            "ROAM-PK-07",
            "Northern Pakistan Grand Circuit (Hunza + Skardu)",
            "Gilgit, Hunza & Baltistan",
            "Pakistan",
            "10 Days / 9 Nights",
            "$1,399",
            "$1,199",
            "June through September (Weekly Departures)",
            "All boutique & resort accommodations, private Toyota Land Cruiser with fuel & mountain driver, all meals (breakfast, lunch, dinner), national park entry fees, cultural folk music night.",
            "Islamabad hotel prior to departure, domestic flight Islamabad-Gilgit (if requested), personal porter fees.",
            "The ultimate northern expedition connecting Hunza's apricot orchards and Karakoram Highway with Skardu's turquoise lakes and Deosai high-altitude plateau.",
            "5.0 / 5.0 (190 reviews) - 'The undisputed ultimate road trip of a lifetime.'"
        ],
        [
            "ROAM-PK-08",
            "Swat Valley & Kalam Alpine Discovery",
            "Swat Valley, Kalam & Malam Jabba",
            "Pakistan",
            "4 Days / 3 Nights",
            "$450",
            "$380",
            "Available Weekly (March through November)",
            "Riverside resort in Fizagat & Kalam, private air-conditioned Prado with driver, daily breakfast & dinner, local guide, Malam Jabba chairlift & zipline passes, Mahodand Lake 4x4 jeep safari.",
            "Lunch meals, personal shopping, optional skiing gear rental.",
            "Explore the Switzerland of the East: Malam Jabba ski slope views, scenic Ushu pine forest walk, turquoise Mahodand Lake excursion, Mingora traditional handicrafts bazaar.",
            "4.9 / 5.0 (260 reviews) - 'Breathtaking green valleys, river views, and fantastic mountain air.'"
        ]
    ]
    
    # Styling colors matching Roamora Travels branding (Navy #0F172A, Teal #0D9488, Gold #D97706)
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    data_font = Font(name="Calibri", size=10)
    data_alignment = Alignment(vertical="center", wrap_text=True)
    price_alignment = Alignment(horizontal="center", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    
    # Write Headers
    ws.row_dimensions[1].height = 32
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
        
    # Write Data Rows
    for row_num, row_data in enumerate(packages, 2):
        ws.row_dimensions[row_num].height = 55
        is_even = (row_num % 2 == 0)
        
        for col_num, cell_value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = cell_value
            cell.font = data_font
            cell.border = thin_border
            
            if is_even:
                cell.fill = zebra_fill
                
            if col_num in [1, 5, 6, 7]:
                cell.alignment = price_alignment
            else:
                cell.alignment = data_alignment

    # Column widths
    col_widths = {
        'A': 16, # Package Code
        'B': 30, # Package Name
        'C': 26, # Destination
        'D': 16, # Country
        'E': 18, # Duration
        'F': 18, # Standard Price
        'G': 18, # Discounted Price
        'H': 32, # Availability & Group Size
        'I': 45, # Included Services
        'J': 35, # Excluded Services
        'K': 50, # Key Highlights & Itinerary
        'L': 42  # Rating & Reviews
    }
    
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width
        
    ws.freeze_panes = "A2"
    
    wb.save(output_path)
    print(f"Successfully generated Roamora Travels Tour Packages catalog at: {output_path}")

if __name__ == "__main__":
    create_travel_packages_excel()
