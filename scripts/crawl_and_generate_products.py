import os
import re
import csv
import random
import urllib.request
import xml.etree.ElementTree as ET
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

os.makedirs("data", exist_ok=True)

print("1. Scraping seed entities from spicemartinc.com...")
sitemap_urls = [
    "https://spicemartinc.com/page-sitemap.xml",
    "https://spicemartinc.com/post-sitemap.xml",
    "https://spicemartinc.com/category-sitemap.xml"
]

live_products = []
live_images = []

for s_url in sitemap_urls:
    try:
        req = urllib.request.Request(s_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            content = response.read()
            root = ET.fromstring(content)
            for url_elem in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None and loc.text:
                    url_text = loc.text
                    if '/products/' in url_text or '/category/' in url_text or '/spices/' in url_text:
                        parts = [p for p in url_text.split('/') if p]
                        if parts:
                            slug = parts[-1].replace('-', ' ').title()
                            slug = re.sub(r'\b\d+\b', '', slug).strip()
                            if slug and slug.lower() not in ['products', 'category', 'spices', 'cart', 'checkout', 'my account']:
                                img_loc = ''
                                img_elem = url_elem.find('{http://www.google.com/schemas/sitemap-image/1.1}image')
                                if img_elem is not None:
                                    img_src = img_elem.find('{http://www.google.com/schemas/sitemap-image/1.1}loc')
                                    if img_src is not None and img_src.text:
                                        img_loc = img_src.text.split('/')[-1]
                                live_products.append({'name': slug, 'image': img_loc})
    except Exception as e:
        print(f"Note on {s_url}: {e}")

print(f"Found {len(live_products)} catalog seed references from spicemartinc.com.")

CATALOG_BLUEPRINT = {
    "Spices & Whole Seeds": {
        "isTaxable": "No",
        "brands": ["SpiceMart Select", "Swad", "Laxmi", "Deep", "Pride of India", "Badia", "El Guapo", "Ziyad", "TRS", "MDH", "Everest", "Rani"],
        "items": [
            ("Whole Black Peppercorns (Tellicherry Special)", "100g", 3.49, "Premium aromatic whole black tellicherry peppercorns with robust heat and citrus aroma."),
            ("Whole Green Cardamom Pods (Elaichi Jumbo)", "200g", 12.99, "Fragrant green cardamom pods handpicked for rich desserts, chai, and savory biryanis."),
            ("Whole Black Cardamom (Badi Elaichi)", "200g", 7.49, "Smoky black cardamom pods essential for slow-cooked curries, dals, and meat dishes."),
            ("Whole Cumin Seeds (Jeera Prime)", "400g", 4.99, "Earthy and aromatic whole cumin seeds, ideal for tadka seasoning, rice, and spice rubs."),
            ("Whole Coriander Seeds (Dhania Sabut)", "400g", 3.99, "Crisp whole coriander seeds with citrusy floral notes for roasting, grinding, and curry bases."),
            ("Whole Mustard Seeds (Brown Rai)", "400g", 2.99, "Pungent brown mustard seeds for South Indian tadka, pickles, and tempering vegetable sautés."),
            ("Whole Yellow Mustard Seeds", "400g", 2.99, "Mild and nutty yellow mustard seeds for pickling, marinades, and relishes."),
            ("Whole Fennel Seeds (Saunf Extra Bold)", "400g", 4.49, "Sweet and aromatic fennel seeds for curries, desserts, digestive mukhwas, and teas."),
            ("Whole Fenugreek Seeds (Methi Dana)", "400g", 3.29, "Bitter-sweet golden fenugreek seeds used in sambhar, pickles, and healthy infusions."),
            ("Whole Star Anise (Chakra Phool)", "150g", 5.99, "Intensely aromatic eight-pointed star anise for biryanis, broths, and spiced stews."),
            ("Whole Cloves (Laung Extra Fresh)", "150g", 6.49, "Highly potent whole cloves with rich essential oils for baking, biryani, and garam masala."),
            ("Cinnamon Sticks (Ceylon True Cinnamon)", "100g", 7.99, "Delicate multi-layered sweet Ceylon cinnamon quills for delicate baking and desserts."),
            ("Cassia Cinnamon Bark (Dalchini Hard Sticks)", "200g", 3.99, "Thick aromatic cassia bark providing warm pungent sweetness in savory curries."),
            ("Mace Blades (Javitri Golden)", "100g", 9.99, "Delicate golden mace flower blades offering nutmeg aroma and vibrant yellow hue."),
            ("Whole Nutmeg (Jaiphal with Shell)", "100g", 5.49, "Whole round nutmeg kernels for fresh grating over desserts, bechamel, and garam masalas."),
            ("Ajwain Carom Seeds (Desi Bishop's Weed)", "200g", 3.49, "Thyme-like aromatic carom seeds for samosa dough, parathas, and digestive cooking."),
            ("Nigella Seeds (Kalonji / Black Cumin)", "200g", 3.99, "Onion-like peppery black seeds for naan bread toppings, pickles, and roasted roots."),
            ("Kashmiri Dried Red Chillies (Stemless)", "200g", 6.99, "Mild heat and rich deep crimson red color for tandoori dishes and rich gravies."),
            ("Guntur Spicy Red Chillies (Whole with Stem)", "400g", 5.99, "Fiery hot red chillies from Andhra Pradesh for authentic spicy regional curries."),
            ("Byadgi Red Chillies (Karnataka Special)", "400g", 6.49, "Crinkled aromatic red chillies with high color index and moderate balanced spice."),
            ("Dried Mexican Guajillo Chiles", "8 oz", 4.99, "Mild-to-medium sweet dried chiles with bright berry undertones for mole, pozole, and salsa."),
            ("Dried Mexican Ancho Chiles (Poblano)", "8 oz", 5.49, "Rich, smoky dried poblano peppers with raisin notes for authentic Mexican enchiladas."),
            ("Dried Mexican Pasilla Chiles (Negro)", "8 oz", 5.49, "Dark wrinkly dried chiles with earthy herbal flavors for classic salsa borracha and mole."),
            ("Dried Mexican Chiles de Arbol", "4 oz", 3.99, "Slender fiery Mexican peppers providing vibrant heat for table salsas and hot sauces."),
            ("Dried Mexican Chipotle Morita Peppers", "8 oz", 5.99, "Smoked dried red jalapeno peppers providing deep smoky complexity to stews and beans."),
            ("Mexican Whole Oregano (Hierba Dulce)", "4 oz", 3.49, "Earthy and citrusy Mexican oregano with robust essential oils for fajitas and chili."),
            ("Epazote Dried Herb (Mexican Tea)", "2 oz", 3.99, "Traditional Latin American herb essential for authentic refried black and pinto beans."),
            ("Sumac Ground Mediterranean Berries", "250g", 4.99, "Tart, lemony crimson berry spice for sprinkling over hummus, fattoush, and grilled kebabs."),
            ("Za'atar Herb Blend with Sesame", "250g", 5.49, "Classic Middle Eastern thyme, sumac, toasted sesame, and sea salt blend for flatbreads."),
            ("Baharat 7-Spice Arabic Seasoning", "200g", 5.99, "All-purpose Middle Eastern aromatic blend of allspice, black pepper, cinnamon, and clove."),
            ("Mahlab Cherry Kernel Seeds", "100g", 8.49, "Aromatic ground sour cherry pits for Middle Eastern breads, ma'amoul, and sweet pastries."),
            ("Whole White Peppercorns (Sarawak)", "200g", 6.49, "Mild, fermented white pepper for creamy soups, light sauces, and Asian broths."),
            ("Allspice Whole Berries (Pimento)", "150g", 4.49, "Clove, cinnamon, and nutmeg spiced Jamaican whole pimento berries for stews and rubs."),
            ("Juniper Berries (Dried Alpine)", "100g", 4.99, "Piny resinous dried berries for marinades, roasts, pickling, and European seasonings."),
            ("White Sesame Seeds (Hulled Til)", "400g", 3.99, "Clean hulled white sesame seeds for tahini, chikki brittle, and stir-fry garnishes."),
            ("Black Sesame Seeds (Unhulled Kala Til)", "400g", 4.29, "Nutty mineral-rich unhulled black sesame seeds for traditional sweets and savory crusts."),
            ("Poppy Seeds White (Khus Khus)", "200g", 6.99, "Nutty white poppy seeds for thickening rich Shahi gravies, kormas, and halwa."),
            ("Dry Bay Leaves (Tejpatta Royal)", "100g", 2.99, "Aromatic Indian Cassia bay leaves with cinnamon notes for biryanis, curries, and soups."),
            ("Panch Phoron (Bengali 5-Spice Blend)", "200g", 3.99, "Equal parts cumin, brown mustard, fenugreek, nigella, and fennel seeds for vegetable tempering."),
            ("Whole Dried Curry Leaves (Kadi Patta)", "50g", 2.49, "Fragrant air-dried curry leaves for authentic South Indian tadka tempering and rasam."),
            ("Dried Mexican Hibiscus Flowers (Flor de Jamaica)", "8 oz", 4.99, "Tart ruby dried hibiscus petals for brewing refreshing Agua de Jamaica and teas."),
            ("Mexican Cinnamon Soft Canela Sticks", "4 oz", 4.49, "Soft crushable Mexican canela quills for Mexican hot chocolate, arroz con leche, and mole."),
            ("Dried Avocado Leaves (Hoja de Aguacate)", "1 oz", 3.99, "Anise-flavored dried avocado leaves used in Oaxacan black bean stews and braises.")
        ]
    },
    "Ground Spices & Masala Blends": {
        "isTaxable": "No",
        "brands": ["SpiceMart", "MDH", "Shan", "Everest", "Badshah", "Catch", "Swad", "Laxmi", "Tajin", "Goya", "Ziyad", "Al Farez"],
        "items": [
            ("Organic Turmeric Powder (High Curcumin 5%)", "500g", 4.99, "Vibrant golden ground turmeric root with high curcumin content for curries and golden milk."),
            ("Kashmiri Deggi Mirch (Color & Mild Heat)", "500g", 5.99, "Rich scarlet red ground pepper imparting stunning crimson hue without overpowering heat."),
            ("Extra Hot Red Chilli Powder (Lal Mirch)", "500g", 4.99, "Pure ground sun-dried red chillies with bold pungent heat for spicy savory dishes."),
            ("Coriander Cumin Powder (Dhana Jeera)", "500g", 4.49, "Classic Gujarati balanced blend of roasted coriander and cumin powders for daily curries."),
            ("Garam Masala Powder (Royal Heritage Blend)", "200g", 4.99, "Warm royal spice blend of cardamom, mace, cinnamon, clove, and pepper for aromatic finish."),
            ("Biryani Masala Powder (Hyderabadi Style)", "100g", 2.49, "Complex aromatic seasoning blend with saffron notes for authentic layered meat and veg biryani."),
            ("Tandoori Chicken Tikka Masala Seasoning", "100g", 2.29, "Tangy and savory spice rub for clay-oven tandoori chicken, paneer tikka, and barbecues."),
            ("Chana Masala Spice Mix (Punjabi Chole)", "100g", 2.29, "Tart pomegranate and mango seasoned spice mix for rich dark Punjabi chickpea curry."),
            ("Pav Bhaji Masala (Mumbai Street Style)", "100g", 2.29, "Authentic street blend with dried mango and fennel for Mumbai style mashed vegetable curry."),
            ("Sambhar Masala Powder (Madras Style)", "200g", 3.49, "Roasted lentil and spice blend for authentic South Indian lentil and vegetable stew."),
            ("Rasam Powder (Traditional Udupi Blend)", "200g", 3.49, "Peppery cumin and coriander seasoning for tangy tomato, tamarind, and lentil rasam soup."),
            ("Chaat Masala (Tangy Street Seasoning)", "200g", 3.49, "Tangy, savory black salt and amchur seasoning for street snacks, fruit salads, and pakoras."),
            ("Amchur Powder (Dry Green Mango)", "200g", 3.99, "Sun-dried raw green mango powder providing fruity tart acidity to samosa fillings and curries."),
            ("Kala Namak (Himalayan Black Rock Salt Powder)", "400g", 2.99, "Mineral-rich volcanic rock salt with distinctive savory umami sulfur aroma for chaats."),
            ("Dry Ginger Powder (Sonth Pure Ground)", "200g", 3.99, "Zesty warm dried ginger powder for chai masala, gingerbread, and Ayurvedic remedies."),
            ("Hing Powder (Asafoetida Compounded Yellow)", "100g", 4.99, "Pungent resin powder providing garlic-onion flavor and digestive benefits to lentil curries."),
            ("Pure Asafoetida Hing Powder (Gluten Free Bandhani)", "50g", 7.99, "Concentrated pure Hing resin powder for sattvic cooking without garlic or onions."),
            ("Mexican Taco Seasoning Mix", "6 oz", 3.29, "Bold savory blend of ancho chile, cumin, garlic, Mexican oregano, and paprika for tacos."),
            ("Fajita Spice Rub Seasoning", "6 oz", 3.29, "Zesty lime, garlic, cumin, and cracked pepper rub for sizzling skillet steak and chicken."),
            ("Authentic Shawarma Spice Seasoning", "200g", 4.49, "Traditional Lebanese spice mix of cardamom, cumin, paprika, coriander, and allspice."),
            ("Shish Taouk Poultry Marinade Mix", "200g", 4.49, "Garlic, citrus, and paprika Mediterranean marinade for tender grilled chicken skewers."),
            ("Madras Curry Powder (Hot & Aromatic)", "400g", 4.99, "World-renowned golden curry blend of turmeric, fenugreek, coriander, and yellow mustard."),
            ("Fish Curry Masala (Goan Coconut & Kokum Style)", "100g", 2.49, "Tangy and spicy coastal seafood seasoning for coconut milk and kokum fish gravies."),
            ("Meat Korma Curry Masala", "100g", 2.49, "Rich, nutty, and creamy mild curry spice mix with cardamom and almond notes for kormas."),
            ("Nihari Masala Seasoning (Slow Cooked Stew)", "100g", 2.49, "Traditional Delhi/Lahori shank stew spice blend with fennel, star anise, and pippali pepper."),
            ("Saffron Strands (Super Negin Grade A Saffron)", "2g", 14.99, "All-red long saffron threads with intense aroma and golden color for biryani and sweets."),
            ("Ras El Hanout (Moroccan Top-Shelf 21 Spice)", "150g", 6.99, "Complex aromatic Moroccan spice blend with rose petals, lavender, cardamom, and clove."),
            ("Dukkah Egyptian Nut & Spice Blend", "150g", 5.99, "Toasted hazelnut, sesame, coriander, and cumin dipping blend for crusty bread and olive oil."),
            ("Ground Ancho Chile Powder (Pure 100%)", "8 oz", 4.99, "Sweet smoky single-origin ground ancho pepper with mild warmth and fruity notes."),
            ("Ground Chipotle Pepper Powder (Smoked Jalapeno)", "8 oz", 5.49, "Deep wood-smoked red jalapeño pepper powder for BBQ rubs, chili, and chipotle mayo."),
            ("Tajin Clásico Chili Lime Seasoning", "14 oz", 4.99, "World-famous Mexican blend of mild chili peppers, sea salt, and dehydrated lime juice.")
        ]
    },
    "Rice, Grains & Flours": {
        "isTaxable": "No",
        "brands": ["Royal", "India Gate", "Laxmi", "Daawat", "Aashirvaad", "Sujata", "Pillsbury", "Maseca", "Swad", "Ziyad", "Goya", "Kohinoor"],
        "items": [
            ("Royal Chef's Secret Extra Long Grain Basmati Rice", "10 lb", 18.99, "Aged Basmati rice grain with remarkable kernel elongation up to 2.5x when cooked."),
            ("India Gate Classic Aged Basmati Rice", "20 lb", 32.99, "Aged for 2 years in Himalayan foothills for pearlescent fluffy grains and sweet aroma."),
            ("Daawat Traditional Basmati Rice", "10 lb", 16.99, "Premium slender fragrant Basmati rice ideal for everyday steamed rice and pulao."),
            ("Laxmi Sona Masoori Rice (Aged South Indian)", "20 lb", 24.99, "Lightweight, low-starch aromatic medium-grain rice perfect for daily South Indian meals."),
            ("Swad Ponni Boiled Rice (Parboiled Thanjavur)", "20 lb", 23.99, "Nutrient-rich parboiled rice from Tamil Nadu for fluffy steamed rice, sambhar, and curd rice."),
            ("Idli & Dosa Rice (Short Grain Parboiled)", "10 lb", 11.99, "Specially milled short-grain parboiled rice yielding soft fluffy idlis and crisp golden dosas."),
            ("Organic Brown Basmati Rice (Whole Grain)", "10 lb", 15.99, "Fiber-rich whole grain brown Basmati with a nutty flavor and satisfying chewy texture."),
            ("Aashirvaad Sharbati Select Whole Wheat Atta", "20 lb", 19.99, "Stone-ground 100% whole wheat flour from MP Sharbati grains for ultra-soft rotis."),
            ("Sujata Gold Premium Whole Wheat Chakki Atta", "20 lb", 18.99, "Traditional stone-milled whole wheat flour locking in natural bran nutrients and taste."),
            ("Laxmi Pure Chana Dal Besan (Gram Flour)", "4 lb", 6.99, "Finely milled yellow gram chickpea flour for pakoras, dhokla, kadhi, and Indian sweets."),
            ("Sooji Rava Coarse (Semolina Wheat Cream)", "4 lb", 5.49, "Granular durum wheat semolina for crispy rava dosas, upma, and sheera halwa."),
            ("Fine Rava (Chiroti Sooji for Sweets)", "4 lb", 5.49, "Micro-fine wheat semolina for flaky puran poli, sooji ladoos, and delicate pastries."),
            ("Maseca Instant Corn Masa Flour (Yellow)", "4.4 lb", 5.99, "Nixtamalized yellow corn masa flour for authentic homemade tortillas, tamales, and pupusas."),
            ("Maseca Instant Corn Masa Flour (White)", "4.4 lb", 5.99, "Classic nixtamalized white corn masa flour for tender soft table tortillas and gorditas."),
            ("Maseca Tamale Corn Flour (Coarse Grind)", "4.4 lb", 6.29, "Specially coarse ground corn masa flour for fluffy, tender, and moist Mexican tamales."),
            ("Goya Jasmine Long Grain Thai Fragrant Rice", "10 lb", 14.99, "Naturally fragrant aromatic Thai Jasmine rice with soft, slightly sticky texture."),
            ("Pearl Couscous (Israeli Toasted Grains)", "2 lb", 4.99, "Toasted wheat semolina pasta pearls for vibrant Mediterranean grain bowls and salads."),
            ("Fine Bulgur Wheat #1 (Tabouli Grade)", "2 lb", 3.99, "Parboiled cracked wheat grain specifically sized for quick-soak authentic Lebanese tabbouleh."),
            ("Coarse Bulgur Wheat #3 (Pilaf Grade)", "2 lb", 3.99, "Hearty parboiled cracked wheat for Turkish bulgur pilaf, soups, and hearty stuffings."),
            ("Freekeh Roasted Green Cracked Wheat", "2 lb", 6.99, "Smoky roasted young green wheat grain packed with plant protein and ancient grain nutrition."),
            ("Jowar Flour (White Sorghum Millet Atta)", "4 lb", 6.49, "Gluten-free nutrient-dense sorghum millet flour for rustic bhakri and rotis."),
            ("Bajra Flour (Pearl Millet Desi Atta)", "4 lb", 6.49, "Iron-rich winter pearl millet flour for hearty traditional Kathiawadi and Rajasthani rotlas."),
            ("Ragi Flour (Finger Millet Nachni Atta)", "4 lb", 6.49, "Calcium-loaded red finger millet flour for healthy mudde, dosas, and baby porridges."),
            ("Poha Thick (Flattened Rice Flakes)", "2 lb", 3.99, "Flattened rice flakes for quick Maharashtrian breakfast Kanda Poha and savory snacks."),
            ("Poha Thin (Nylon Flattened Rice)", "2 lb", 3.99, "Delicate thin rice flakes for quick roasted diet chivda namkeen with peanuts and curry leaves."),
            ("Sabudana Tapioca Pearls (Large Sago)", "2 lb", 4.49, "Plump starch pearls for fasting dishes like Sabudana Khichdi, vadas, and sweet kheer."),
            ("Goya Long Grain White Enriched Rice", "20 lb", 19.99, "Fluffy non-sticky enriched long grain rice, a staple for Arroz con Pollo and Caribbean beans."),
            ("Royal Organic White Quinoa Grain", "4 lb", 9.99, "Pre-washed organic complete protein ancient Andean quinoa seeds for salads and bowls.")
        ]
    },
    "Lentils, Dals & Pulses": {
        "isTaxable": "No",
        "brands": ["Laxmi", "Swad", "Deep", "24 Mantra Organic", "Goya", "Ziyad", "Al Wadi", "TRS", "Natco"],
        "items": [
            ("Toor Dal Oily (Arhar Split Pigeon Peas)", "4 lb", 7.99, "Naturally preserved with castor oil for freshness, yielding rich authentic Gujarati/South Indian dal."),
            ("Toor Dal Plain Non-Oily (Split Yellow Pigeon Peas)", "4 lb", 7.49, "Clean dry-split pigeon peas that cook into creamy golden tadka dal and sambhar."),
            ("Moong Dal Yellow Split (Skinless)", "4 lb", 6.99, "Quick-cooking tender yellow split mung lentils, light on digestion for khichdi and halwa."),
            ("Whole Green Moong Beans (Sabut Moong)", "4 lb", 6.99, "Whole green mung beans ideal for nutritious sprouting, hearty soups, and whole dal curries."),
            ("Moong Dal Chilka (Split with Green Skin)", "4 lb", 6.99, "Split mung lentils with fiber-rich skin intact for crispy moong dal pakodas and cheela."),
            ("Chana Dal (Split Desi Chickpeas)", "4 lb", 5.99, "Nutty split baby chickpeas for dhokla batter, dal fry, and puran poli stuffing."),
            ("Kabuli Chana (Jumbo Garbanzo Chickpeas)", "4 lb", 6.99, "Extra large white chickpeas that cook to buttery tenderness for Punjabi Chole and hummus."),
            ("Kala Chana (Small Brown Desi Chickpeas)", "4 lb", 5.99, "Flavorful nutrient-dense dark brown chickpeas for festive dry Prasad chana and Kerala curry."),
            ("Urad Dal White Whole (Gota for Idli/Dosa)", "4 lb", 7.99, "Whole skinned white urad beans that grind to maximum volume and aeration for idli batter."),
            ("Urad Dal Split White (Dhuli)", "4 lb", 7.49, "Split skinned white lentils for creamy dal makhani components and papad making."),
            ("Urad Dal Black Whole (Sabut for Dal Makhani)", "4 lb", 6.99, "Hearty whole black lentils slow-simmered with butter and cream for authentic Dal Makhani."),
            ("Masoor Dal Red Split (Quick Cook Egyptian)", "4 lb", 5.99, "Quick-dissolving orange lentils that turn golden yellow when cooked into comforting dal soup."),
            ("Whole Brown Masoor (Sabut Brown Lentils)", "4 lb", 5.99, "Earthy whole brown lentils with firm skins that hold shape in stews and spiced khichdi."),
            ("Rajma Dark Red Kidney Beans (Jammu Grade)", "4 lb", 7.49, "Plump dark red kidney beans that yield a rich thick gravy for authentic Punjabi Rajma."),
            ("Rajma Chitra (Speckled Himalayan Kidney Beans)", "4 lb", 7.49, "Tender cream-colored speckled kidney beans from Kashmir that cook faster with silky texture."),
            ("Black Eyed Peas (Lobia / Chawli)", "4 lb", 5.49, "Creamy white cowpeas with dark spots, quick cooking for curries and Southern braised beans."),
            ("Dried Fava Beans Whole (Ful Medames Grade)", "2 lb", 4.49, "Traditional broad fava beans for slow-cooking Egyptian national Ful Medames breakfast."),
            ("Dried Fava Beans Split (Habas Peladas)", "2 lb", 4.49, "Skinned split fava beans for Middle Eastern falafel patties and Mediterranean puree soups."),
            ("Goya Dry Pinto Beans (Frijoles Pintos)", "4 lb", 5.99, "Essential mottled pinto beans for making homemade Mexican refried beans and bean burritos."),
            ("Goya Dry Black Beans (Frijoles Negros)", "4 lb", 5.99, "Nutrient-rich black beans for Cuban black bean soup, Mexican side beans, and rice bowls."),
            ("Goya Dry Red Small Beans (Frijoles Rojos)", "4 lb", 5.99, "Small silky red beans traditional for Central American Casamiento and red bean stew."),
            ("Moth Beans Whole (Turkish Gram / Matki)", "4 lb", 6.49, "Tiny brown drought-hardy beans used for sprouting in Maharashtrian Misal Pav and USAL."),
            ("Green Split Peas (Matar Dal)", "4 lb", 4.99, "Sweet split dried green peas for hearty split pea soup and Bengali dry ghugni curries."),
            ("Yellow Split Peas", "4 lb", 4.99, "Mild yellow split field peas for yellow split pea stews, dhal, and Mediterranean dips.")
        ]
    },
    "Cooking Oils, Ghee & Pastes": {
        "isTaxable": "No",
        "brands": ["Amul", "Gowardhan", "Aashirvaad", "Swad", "Patanjali", "Dabur", "Idhayam", "Goya", "Ziyad", "Al Wadi", "Crisco"],
        "items": [
            ("Amul Pure Cow Ghee (Clarified Butter Tin)", "1 L", 15.99, "Traditional rich granular golden cow ghee made from fresh dairy cream with nutty aroma."),
            ("Gowardhan 100% Pure Cow Ghee Jar", "1 L", 16.49, "Rich, aromatic cow ghee packed in a convenient wide-mouth jar for rotis, dal, and sweets."),
            ("Aashirvaad Svasti Pure Cow Ghee", "1 L", 15.99, "Special slow-cook process ghee with distinct aroma and granular texture for daily dining."),
            ("Swad Pure Buffalo Milk Ghee (White)", "32 oz", 14.99, "High smoke-point pure buffalo ghee with smooth body and rich flavor for deep frying sweets."),
            ("Idhayam Pure Gingelly Sesame Oil", "1 L", 9.99, "Cold-pressed traditional South Indian sesame oil with nutty aroma for pickles and dosas."),
            ("KTC Pure Mustard Oil (Sarson Ka Tel)", "1 L", 7.49, "Pungent cold-pressed mustard oil essential for North Indian and Bengali fish and vegetable curries."),
            ("Parachute 100% Pure Edible Coconut Oil", "1 L", 9.49, "Made from sun-dried ripe copra coconuts for authentic Kerala seafood curries and avial."),
            ("Swad Pure Cold Pressed Peanut Groundnut Oil", "2 L", 14.99, "High smoke point nutty groundnut oil ideal for Gujarati cooking, snacks, and deep frying."),
            ("Ziyad Extra Virgin Lebanese Olive Oil (Cold Extracted)", "1 L", 13.99, "First cold-pressed Mediterranean olive oil with peppery finish for hummus and dressings."),
            ("Goya Pure Extra Virgin Olive Oil", "1 L", 12.99, "Rich fruity olive oil imported from Spain for Mediterranean, Latin, and grilled recipes."),
            ("Dabur Hommade Ginger Garlic Paste", "400g", 3.99, "Freshly blended ginger and garlic in balanced ratio for instant flavor in curries and marinades."),
            ("Swad Pure Garlic Paste (No Preservatives)", "300g", 3.49, "Pure peeled garlic paste ready for stir-fries, marinades, pasta sauces, and curries."),
            ("Swad Pure Ginger Paste", "300g", 3.49, "Aromatic zesty ginger puree saving prep time for teas, curries, and dressings."),
            ("Tamicon Pure Tamarind Concentrate Paste", "400g", 4.49, "Thick seedless tart tamarind pulp for tangy sambhar, rasam, chutneys, and Thai pad thai."),
            ("San Marcos Chipotle Peppers in Adobo Sauce", "7 oz", 2.49, "Smoky roasted chipotle chilies in rich tangy tomato and vinegar adobo sauce."),
            ("Cortas Pure Pomegranate Molasses (Dibs Ruman)", "300 ml", 5.49, "Tart and sweet boiled pomegranate reduction for muhammara dip, marinades, and fattoush."),
            ("Al Wadi Al Akhdar Pure Lebanese Tahini Paste", "1 lb", 6.99, "100% ground Ethiopian sesame seed paste for silky smooth restaurant-quality hummus."),
            ("Ziyad Premium Creamy Hummus Tahina Spread", "14 oz", 3.99, "Velvety sesame tahina and chickpea spread ready to serve with warm pita and olive oil.")
        ]
    },
    "Pickles, Chutneys & Sauces": {
        "isTaxable": "No",
        "brands": ["Mother's Recipe", "Priya", "Bedekar", "Ahmed", "Herdez", "La Costeña", "El Pato", "Ziyad", "Deep", "Swad"],
        "items": [
            ("Mother's Recipe Punjabi Mango Pickle (Aam Achar)", "500g", 4.49, "Spicy raw green mango pieces cured in mustard oil with fennel, kalonji, and fenugreek."),
            ("Priya Gongura Pickle with Garlic (Andhra Special)", "300g", 3.99, "Tangy sorrel leaf gongura paste with spicy red chillies, mustard oil, and garlic cloves."),
            ("Priya Avakaya Mango Pickle with Garlic", "300g", 3.99, "Traditional fiery Andhra cut raw mango pickle seasoned with mustard powder and red chili."),
            ("Mother's Recipe Lime Sweet & Sour Pickle (Nimbu)", "500g", 4.49, "Sun-ripened yellow juicy lemons cured with spices and sugar for sweet-tangy balance."),
            ("Bedekar Mixed Vegetable Pickle in Mustard Oil", "400g", 4.49, "Crunchy carrots, cauliflower, turnip, and raw mangoes in aromatic Maharashtrian spices."),
            ("Priya Green Chilli Paste Pickle with Tamarind", "300g", 3.99, "Hot green serrano chillies stone-ground with tangy tamarind and toasted mustard seeds."),
            ("Ahmed Mixed Pickle in Oil (Hyderabadi Style)", "1 kg", 6.99, "Large party jar of seasoned mango, lime, carrot, and green chilli pickles."),
            ("Swad Mint & Coriander Chutney (Sandwich Dip)", "300g", 3.49, "Refreshing bright green herbaceous chutney for samosas, chaat, and toasted sandwiches."),
            ("Swad Sweet Date & Tamarind Chutney (Meethi)", "300g", 3.49, "Sweet and tangy dipping sauce made with ripe dates, jaggery, and tamarind for chaats."),
            ("Deep Spicy Schezwan Chutney Dip", "250g", 3.49, "Indo-Chinese fiery garlic, red chilli, and ginger dipping sauce for momos and fried rice."),
            ("Herdez Salsa Verde (Medium Tomatillo Sauce)", "16 oz", 3.99, "Tangy fire-roasted green tomatillos, jalapeños, onions, and cilantro for chips and enchiladas."),
            ("Herdez Salsa Casera (Mild Chunky Red Salsa)", "16 oz", 3.99, "Classic chunky red salsa with ripe tomatoes, onions, serrano peppers, and fresh cilantro."),
            ("La Costeña Pickled Jalapeño Nacho Slices", "26 oz", 3.99, "Crisp sliced pickled jalapeños with carrot slices and onions in spiced pickling brine."),
            ("El Pato Hot Tomato Sauce with Jalapeno (Yellow Can)", "7.75 oz", 1.49, "Iconic spicy tomato dipping sauce for Mexican enchiladas, tacos, rice, and eggs."),
            ("La Costeña Green Enchilada Sauce", "15 oz", 2.99, "Ready-to-use tangy green tomatillo sauce seasoned with garlic, cilantro, and chile."),
            ("Harissa Spicy Red Pepper Paste (North African)", "200g", 4.99, "Fiery Tunisian red chile pepper paste with garlic, caraway, coriander, and olive oil."),
            ("Ziyad Shatta Fiery Mediterranean Hot Pepper Sauce", "10 oz", 3.99, "Crushed red hot peppers with vinegar and salt for Mediterranean shawarma and grilled meats.")
        ]
    },
    "Snacks, Namkeen & Bakery": {
        "isTaxable": "Yes",
        "brands": ["Haldiram's", "Bikaji", "Balaji", "Bikanervalo", "Deep", "Mission", "Takis", "Barcel", "Ziyad", "Alkanater"],
        "items": [
            ("Haldiram's Nagpur Aloo Bhujia Spicy Potato Sev", "400g", 4.49, "Crispy fried potato and moth bean vermicelli seasoned with mint, dry mango, and spices."),
            ("Haldiram's Classic Bhujia Sev (Bikaneri)", "400g", 4.49, "Traditional moth bean and gram flour crunchy noodles with black pepper and clove warmth."),
            ("Haldiram's All in One Crunchy Mixture", "400g", 4.49, "Savory medley of lentils, nuts, raisins, cornflakes, and crunchy sev namkeen."),
            ("Bikaji Plain Salted Banana Chips (Kerala Style)", "200g", 3.99, "Wafer-thin raw green Nendran plantain slices deep fried in pure coconut oil."),
            ("Deep Methi Khakhra (Crispy Whole Wheat Crackers)", "200g", 2.99, "Vacuum-packed roasted thin Gujarati flatbread crackers spiced with dried fenugreek leaves."),
            ("Deep Masala Khakhra (Roasted Spiced Crackers)", "200g", 2.99, "Crisp toasted wheat crackers with red chili, turmeric, and cumin for tea-time snacking."),
            ("Haldiram's Murukku (South Indian Spiral Rings)", "200g", 3.49, "Crunchy spiral rice and urad flour snacks seasoned with sesame seeds and asafoetida."),
            ("Bikaji Punjabi Tadka Spicy Potato Sticks", "200g", 2.99, "Thick crunchy potato noodles tossed in hot North Indian spice blend and dried mango."),
            ("Haldiram's Khatta Meetha Sweet & Sour Mix", "400g", 4.49, "Crunchy fried green peas, sev, rice flakes, and gram noodles with sweet and tangy glaze."),
            ("Mission Crispy Restaurant Style Tortilla Chips", "13 oz", 3.99, "Light, crispy stone-ground yellow corn tortilla triangles for dipping in salsa and guacamole."),
            ("Takis Fuego Rolled Tortilla Chips (Hot Chili & Lime)", "9.9 oz", 4.29, "Intensely crunchy rolled corn tortilla snack bursting with fiery chili pepper and tangy lime."),
            ("Ziyad Crispy Baked Zaatar Pita Chips", "8 oz", 3.99, "Twice-baked authentic pita bread chips tossed in olive oil, sumac, and wild thyme."),
            ("Alkanater Fresh Handmade Baklava Assortment", "500g", 14.99, "Flaky filo pastry layers packed with crushed pistachios, cashews, and rose syrup."),
            ("Bikano Premium Elaichi Toast Rusk (Crispy Tea Toast)", "400g", 3.49, "Twice-baked crispy wheat bread toasts delicately infused with aromatic green cardamom."),
            ("Parle-G Original Glucose Biscuits", "800g Value Pack", 4.49, "World's most beloved crispy golden milk and wheat tea-time dipping biscuits.")
        ]
    },
    "Sweets, Desserts & Confectionery": {
        "isTaxable": "Yes",
        "brands": ["Haldiram's", "Bikano", "Deep", "De la Rosa", "Lucas", "Pelon", "Ziyad", "Gits", "MTR"],
        "items": [
            ("Haldiram's Gulab Jamun in Rose Saffron Sugar Syrup", "1 kg Tin", 8.99, "Soft melt-in-mouth reduced milk dough balls soaked in aromatic cardamom and rose syrup."),
            ("Haldiram's Sponge Rasgulla (Kolkata Style)", "1 kg Tin", 8.99, "Spongy, juicy fresh chenna cottage cheese dumplings floating in light clarified sugar syrup."),
            ("Haldiram's Royal Soan Papdi with Pistachio & Almond", "500g", 6.49, "Delicate flaky spun sugar and chickpea flour dessert garnished with crushed dry nuts."),
            ("Bikano Premium Kaju Katli (Pure Cashew Fudge)", "400g", 12.99, "Rich, smooth diamond-cut cashew nut fudge crafted with silver vark foil."),
            ("Deep Motichoor Ladoo (Pure Desi Ghee)", "400g", 7.99, "Melt-in-mouth tiny golden gram flour pearls fried in ghee and bound with saffron syrup."),
            ("Haldiram's Kaju Pista Roll (Cashew Pistachio)", "400g", 13.99, "Cylindrical cashew fudge rolls stuffed with crushed roasted emerald pistachio filling."),
            ("Gits Instant Gulab Jamun Dessert Mix", "200g Box", 2.99, "Easy step-by-step dry dessert mix yielding 25 soft, perfect homemade gulab jamuns."),
            ("Gits Instant Jalebi Mix with Squeezer Bottle", "100g", 2.99, "Instant dessert mix for crispy, juicy pretzel-shaped jalebis with dispenser included."),
            ("MTR Instant Badam Drink Almond Milk Mix", "200g", 3.99, "Crushed almond, saffron, and cardamom beverage powder for warm or chilled badam milk."),
            ("Ziyad Pistachio Turkish Delight (Lokum Cubes)", "400g", 6.99, "Soft chewy starch confections loaded with whole roasted pistachios and powdered sugar."),
            ("De La Rosa Mazapán Peanut Marzipan Confection", "12 Count Pack", 4.99, "Classic crumbly melt-in-the-mouth Mexican triple-refined toasted peanut confection."),
            ("Pelon Pelo Rico Tamarind Push Candy", "12 Pack", 5.99, "Fun squeezable tangy and spicy soft Mexican tamarind pulp candy."),
            ("Lucas Muecas Mango Lollipop with Chili Powder", "10 Pack", 4.99, "Sweet mango flavored lollipop with a chili powder dipping pot.")
        ]
    },
    "Middle Eastern Specialties": {
        "isTaxable": "No",
        "brands": ["Ziyad", "Cortas", "Al Wadi", "Cedar", "Midamar", "Sadaf", "Alkanater"],
        "items": [
            ("Cortas Pure Orange Blossom Flower Water (Mazaher)", "300 ml", 4.49, "Distilled floral orange blossom water for Middle Eastern puddings, baklava, and teas."),
            ("Cortas Pure Rose Water (Maward)", "300 ml", 4.49, "Steam-distilled fragrant Lebanese rose petal water for syrups, desserts, and lassi."),
            ("Al Wadi Stuffed Grape Leaves with Rice (Dolmas)", "400g Can", 4.99, "Tender Mediterranean vine leaves rolled around seasoned rice, onion, mint, and olive oil."),
            ("Ziyad Pickled Wild Cucumbers in Brine (Mikti)", "32 oz", 5.49, "Crunchy small Lebanese wild pickled cucumbers with garlic and whole dill."),
            ("Cedar Mediterranean Green Olives with Thyme & Oil", "1 kg", 8.99, "Whole cracked green olives marinated in extra virgin olive oil, wild zaatar, and lemon."),
            ("Alkanater Pure Halva Plain Block with Sesame", "1 lb", 6.49, "Traditional crumbly tahini sesame confection sweetened with pure cane sugar."),
            ("Alkanater Pistachio Halva (Halawa Bil Fustuq)", "1 lb", 7.99, "Classic tahini fudge block embedded with whole roasted Turkish green pistachios."),
            ("Midamar Mediterranean Falafel Quick Dry Mix", "12 oz", 3.49, "Seasoned fava bean and chickpea dry mix for frying golden crisp falafel balls."),
            ("Ziyad Premium Roasted Eggplant Puree (Baba Ghanoush Base)", "18 oz", 4.49, "Fire-roasted peeled eggplant pulp with rich smoky aroma for making fresh Baba Ghanoush."),
            ("Ziyad Arabic Style Cardamom Turkish Coffee (Medium Roast)", "250g", 6.49, "Finely ground Arabica coffee beans blended with fragrant green cardamom for ibrik brewing.")
        ]
    },
    "Mexican & Latin Specialties": {
        "isTaxable": "No",
        "brands": ["Goya", "La Costeña", "San Marcos", "Herdez", "El Guapo", "Cacique", "Jarritos", "Knorr"],
        "items": [
            ("San Marcos Whole Pickled Jalapeño Chiles", "26 oz Can", 3.49, "Whole plump green jalapeños in spiced vinegar brine with carrots and onions."),
            ("La Costeña Refried Pinto Beans (Frijoles Refritos)", "16 oz", 2.29, "Slow-cooked mashed pinto beans seasoned with onion and spices, ready to warm and serve."),
            ("La Costeña Refried Black Beans (Frijoles Negros)", "16 oz", 2.29, "Smooth seasoned Mexican refried black beans for tostadas, burritos, and breakfast eggs."),
            ("Goya Tender Cut Green Cactus Pads (Nopalitos)", "30 oz Jar", 4.49, "Tender sliced prickly pear cactus pads in mild brine for Mexican salads and scramble."),
            ("El Guapo Whole Dried Penca De Maguey (Agave Leaf)", "2 Pack", 5.99, "Sun-cured agave leaves for wrapping authentic slow-steamed Mexican Barbacoa meats."),
            ("El Guapo Corn Husks for Tamales (Hojas para Tamales)", "8 oz", 4.99, "Selected pliable dried corn husks cleaned and ready for wrapping homemade tamales."),
            ("Knorr Granulated Tomato Bouillon with Chicken Flavor", "35.3 oz", 6.99, "Latin American essential seasoning powder for Arroz Rojo, soups, stews, and beans."),
            ("Cacique Ranchero Queso Fresco Fresh Crumbling Cheese", "10 oz", 4.49, "Soft, milky, slightly salted fresh Mexican cheese for crumbling over tacos and beans."),
            ("Cacique Cotija Aged Firm Mexican Grating Cheese", "10 oz", 5.49, "Robust, salty, aged dry cheese ideal for street corn Elote, beans, and enchiladas."),
            ("La Banderita Soft Flour Tortillas (Taco Size 10 Pack)", "16 oz", 3.29, "Tender, pliable flour tortillas perfect for table tacos, quesadillas, and wraps.")
        ]
    },
    "Beverages, Teas & Coffees": {
        "isTaxable": "Yes",
        "brands": ["Wagh Bakri", "Tata Tea", "Red Label", "Brooke Bond", "Taj Mahal", "Hamdard", "Jarritos", "Limca", "Thums Up", "Maaza"],
        "items": [
            ("Wagh Bakri Premium CTC Black Tea", "1 kg Bag", 10.99, "Strong, robust Assam CTC tea granules brewing a bold, rich reddish-amber cup of chai."),
            ("Tata Tea Gold (Assam CTC with Long Leaves)", "1 kg", 12.49, "Blend of rich Assam CTC granules with 15% gently rolled long tea leaves for aroma."),
            ("Brooke Bond Red Label Natural Care Masala Tea", "1 kg", 11.99, "Black tea infused with 5 Ayurvedic herbs: Tulsi, Ashwagandha, Mulethi, Ginger, and Cardamom."),
            ("Brooke Bond Taj Mahal Royal Fine Leaf Tea", "500g", 8.99, "Exquisite whole tea leaves carefully chosen for discerning connoisseurs who prize aroma."),
            ("Hamdard Rooh Afza Herbal Rose Beverage Sharbat", "800 ml Bottle", 5.99, "Iconic cooling summer refresher concentrate made with rose, mint, fruits, and herbal extracts."),
            ("Thums Up Indian Cola Soft Drink (Toofani Taste)", "6 Pack 300ml Cans", 7.99, "Spicy, bold, and heavily carbonated iconic Indian cola with distinct masala fizz."),
            ("Limca Lemon-Lime Fizzy Indian Soda", "6 Pack 300ml Cans", 7.99, "Cloudy, refreshing citrus lemon-lime carbonated soft drink with a zesty punch."),
            ("Maaza Mango Fruit Drink (Alphonso Juice)", "1.2 L Bottle", 4.99, "Thick, luscious real mango pulp beverage capturing the authentic taste of ripe Alphonso mangoes."),
            ("Jarritos Natural Flavored Mexican Soda (Mandarin)", "12.5 oz Bottle", 1.99, "Real sugar carbonated Mexican soda with sweet, refreshing natural mandarin citrus flavor."),
            ("Jarritos Natural Flavored Mexican Soda (Tamarind)", "12.5 oz Bottle", 1.99, "Traditional tangy and sweet Mexican tamarind flavored real sugar glass bottle soda."),
            ("Jarritos Natural Flavored Mexican Soda (Pineapple)", "12.5 oz Bottle", 1.99, "Tropical sweet pineapple soda made with 100% natural Mexican cane sugar."),
            ("Ziyad Cardamom Infused Arabic Black Tea Bags", "100 Count Box", 6.99, "Fine Ceylon black tea blended with crushed natural cardamom pods in tagless bags.")
        ]
    },
    "Dairy, Frozen Foods & Ready to Eat": {
        "isTaxable": "No",
        "brands": ["Amul", "Haldiram's", "Deep", "Swad", "Nanak", "Goya", "MTR", "Ashoka", "Kitchens of India"],
        "items": [
            ("Amul Malai Paneer Block (Fresh Frozen Cottage Cheese)", "400g", 5.99, "Soft, creamy cottage cheese made from pure buffalo milk, perfect for paneer butter masala."),
            ("Nanak Pure Malai Paneer Cubes (Pre-cut)", "1 kg", 11.99, "Pre-diced creamy paneer cubes ready to add directly to curries, gravies, and tandoori skewers."),
            ("Haldiram's Punjabi Samosa with Mint Chutney", "8 Pieces / 650g", 6.49, "Crispy flaky pastry triangles stuffed with spiced potatoes, green peas, and cashews."),
            ("Deep Indian Homestyle Plain Paratha (Layered)", "5 Pack / 400g", 3.99, "Multi-layered flaky unleavened Indian flatbread ready to toast on a skillet in 2 minutes."),
            ("Deep Methi Paratha (Fenugreek Stuffed Flatbread)", "5 Pack / 400g", 4.29, "Savory layered whole wheat flatbread loaded with fresh aromatic fenugreek leaves."),
            ("Deep Aloo Paratha (Spiced Potato Stuffed)", "4 Pack / 400g", 4.49, "Hearty whole wheat flatbread generously filled with seasoned mashed potatoes and herbs."),
            ("Haldiram's Garlic Tandoori Naan (Clay Oven Baked)", "4 Pack / 320g", 3.99, "Authentic flame-baked tandoori naan bread topped with roasted garlic and fresh coriander."),
            ("MTR Ready to Eat Paneer Butter Masala Curry", "300g Pouch", 3.29, "Tender paneer cubes in rich tomato, butter, and cashew gravy. Heat and eat in 90 seconds."),
            ("MTR Ready to Eat Palak Paneer (Spinach Cottage Cheese)", "300g Pouch", 3.29, "Cottage cheese simmered in smooth, delicately spiced spinach puree. 100% natural."),
            ("Ashoka Ready to Eat Dal Tadka with Yellow Lentils", "280g Pouch", 2.99, "Homestyle yellow lentils tempered with garlic, cumin, tomatoes, and green chillies."),
            ("Kitchens of India Royal Dal Makhani (Black Lentil)", "285g Pouch", 3.49, "Slow-simmered black lentils and kidney beans enriched with dairy butter and cream."),
            ("Goya Frozen Whole Yuca Roots (Cassava)", "2 lb Bag", 3.99, "Peeled and cut ready-to-boil or fry tender starchy cassava roots for Latin side dishes."),
            ("Goya Frozen Ripe Plantain Slices (Plátanos Maduros)", "2 lb Bag", 4.99, "Naturally sweet golden ripe plantain slices ready to pan-fry or air-fry for Latin meals.")
        ]
    }
}

PACK_SIZES = [
    ("100g", 0.65), ("200g", 1.0), ("400g", 1.7), ("500g", 2.0),
    ("1 kg", 3.4), ("2 lb", 3.1), ("4 lb", 5.8), ("5 lb", 6.9),
    ("10 lb", 12.5), ("20 lb", 23.0), ("8 oz", 1.1), ("16 oz", 1.8),
    ("32 oz", 3.2), ("1 L", 2.6), ("2 L", 4.8), ("5 L", 10.5),
    ("Pack of 2", 1.9), ("Pack of 3", 2.7), ("Pack of 6", 5.2),
    ("12 Count Box", 4.5), ("24 Count Box", 8.2), ("Economy Case", 15.0)
]

ADJECTIVES = [
    "Premium", "Organic", "Royal", "Selected", "Authentic", "Export Quality",
    "Handpicked", "Aged", "Traditional", "Pure", "Artisanal", "Stone-Ground",
    "Cold-Pressed", "Himalayan", "Coastal", "Desi", "Gourmet", "Farm Fresh"
]

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text[:60]

print("2. Generating structured, unique dataset of at least 6,000 products...")

all_products = []
seen_names = set()

# Populate from blueprint
for category, cat_data in CATALOG_BLUEPRINT.items():
    is_taxable = cat_data["isTaxable"]
    brands = cat_data["brands"]
    items = cat_data["items"]
    
    for item_tuple in items:
        base_name, base_qty, base_price, base_desc = item_tuple
        
        for b_idx, brand in enumerate(brands):
            # Variant 1: Standard Brand + Base Item
            prod_name = f"{brand} {base_name}"
            if prod_name not in seen_names:
                seen_names.add(prod_name)
                inv = random.randint(15, 350)
                price = round(base_price * random.uniform(0.92, 1.15), 2)
                pic_name = f"{slugify(brand)}_{slugify(base_name)}.jpg"
                desc = f"{brand} {base_desc}"
                all_products.append({
                    "Name of the Product": prod_name,
                    "Quantity": base_qty,
                    "Category": category,
                    "Inventory": inv,
                    "Price": f"${price:.2f}",
                    "Product Description": desc,
                    "Picture Name": pic_name,
                    "isTaxable": is_taxable
                })
            
            # Variant 2: Pack size and grade expansions
            for (p_size, p_multiplier) in PACK_SIZES[:12]:
                adj = random.choice(ADJECTIVES)
                extended_name = f"{brand} {adj} {base_name} ({p_size})"
                if extended_name not in seen_names:
                    seen_names.add(extended_name)
                    inv = random.randint(10, 400)
                    calc_price = round(max(1.29, base_price * p_multiplier * random.uniform(0.90, 1.10)), 2)
                    pic_name = f"{slugify(brand)}_{slugify(base_name)}_{slugify(p_size)}.jpg"
                    desc = f"{adj} quality {base_name.lower()} packaged in a {p_size} sealed freshness pack by {brand}. {base_desc}"
                    all_products.append({
                        "Name of the Product": extended_name,
                        "Quantity": p_size,
                        "Category": category,
                        "Inventory": inv,
                        "Price": f"${calc_price:.2f}",
                        "Product Description": desc,
                        "Picture Name": pic_name,
                        "isTaxable": is_taxable
                    })

print(f"Blueprint generated {len(all_products)} products.")

# Ensure we reach > 6,200 products
if len(all_products) < 6200:
    print("Expanding additional specialized lines to guarantee >6,000 items...")
    extra_roots = [
        ("Kalonji Black Seed Infusion Oil", "Cooking Oils, Ghee & Pastes", "No", 8.99, "Cold-pressed pure black seed nigella sativa culinary oil."),
        ("Raw Wildflower Honey with Honeycomb", "Sweets, Desserts & Confectionery", "Yes", 9.99, "100% pure unfiltered raw wildflower honey with natural cut honeycomb piece."),
        ("Organic Jaggery Powder (Desi Shakkar)", "Sweets, Desserts & Confectionery", "No", 4.99, "Unrefined pure sugarcane jaggery powder, natural mineral sweetener."),
        ("Kolhapuri Extra Hot Chilli Powder", "Ground Spices & Masala Blends", "No", 4.99, "Fiery deep red sun-dried Kolhapuri chillies ground with stalks for fierce curries."),
        ("Reshampatti Whole Mild Chillies", "Spices & Whole Seeds", "No", 5.49, "Broad aromatic mild chillies perfect for pickling and Gujarati snacks."),
        ("Guntur Sannam Hot Stemless Chillies", "Spices & Whole Seeds", "No", 5.99, "High capsaicin hot chillies from Andhra Pradesh for authentic fiery dishes."),
        ("Salem High Curcumin Whole Turmeric Fingers", "Spices & Whole Seeds", "No", 4.49, "Unpolished hard Salem turmeric roots with deep golden orange interior."),
        ("Alleppey Finger Turmeric (Kerala Grade)", "Spices & Whole Seeds", "No", 4.99, "High essential oil whole turmeric roots from coastal Alleppey."),
        ("Coorg Black Pepper Bold MG1", "Spices & Whole Seeds", "No", 6.49, "Estate-grown Malabar black peppercorns from high altitude Coorg plantations."),
        ("Wayanad White Pepper Whole Cleaned", "Spices & Whole Seeds", "No", 7.99, "Naturally soaked and de-hulled Malabar pepper berries with delicate aroma."),
        ("Sri Lankan Sweet Cinnamon Ground Powder", "Ground Spices & Masala Blends", "No", 5.99, "True Ceylon cinnamon ground powder for gourmet pastries and drinks."),
        ("Alphonso Mango Pulp Sweetened", "Sweets, Desserts & Confectionery", "No", 5.49, "Canned sweet Ratnagiri Alphonso mango pulp for mango lassi and aamras."),
        ("Kesar Mango Pulp (Gujarat Select)", "Sweets, Desserts & Confectionery", "No", 5.49, "Fragrant golden Kesar mango fruit puree for puddings, ice creams, and desserts."),
        ("Pickled Garlic Pods in Spiced Oil", "Pickles, Chutneys & Sauces", "No", 4.99, "Crisp whole peeled garlic cloves preserved in mustard oil and fenugreek."),
        ("Stuffed Red Chilli Pickle (Banarasi Bharwa Mirch)", "Pickles, Chutneys & Sauces", "No", 5.99, "Large red chillies hand-stuffed with aromatic roasted mustard and amchur masala."),
        ("Pani Puri Pellets Ready to Fry", "Snacks, Namkeen & Bakery", "Yes", 3.49, "Crispy semolina and wheat dry coin discs that puff into round hollow puris."),
        ("Pani Puri Spiced Mint Concentrate Paste", "Pickles, Chutneys & Sauces", "No", 3.99, "Tangy spiced mint, green chilli, and black salt paste for street food Pani Puri."),
        ("Roasted Salted Pistachios in Shell", "Snacks, Namkeen & Bakery", "Yes", 9.99, "Jumbo California pistachios dry roasted and lightly salted with sea salt."),
        ("Raw Cashew Nuts Whole (W240 Grade)", "Snacks, Namkeen & Bakery", "No", 11.99, "Plump jumbo whole cashew nuts for snacking, cooking, and royal gravies."),
        ("Mamra Almonds Iranian (High Oil Content)", "Snacks, Namkeen & Bakery", "No", 16.99, "Premium Iranian Mamra almonds loaded with natural oils and nutrition."),
        ("Makhana Fox Nuts (Puffed Lotus Seeds)", "Snacks, Namkeen & Bakery", "No", 6.99, "Light and crispy roasted lotus seeds packed with plant protein and fiber."),
        ("Dry Coconut Halves (Copra / Sukha Nariyal)", "Spices & Whole Seeds", "No", 4.49, "Cleaned whole dried copra coconut cups for grating into masala pastes and sweets.")
    ]
    
    brand_pool = ["SpiceMart Heritage", "Swad Select", "Laxmi Prime", "Deep Gourmet", "Royal Reserve", "Ziyad Traditional", "Goya Select", "Nirav", "Shalimar", "Golden Temple"]
    
    for r_idx, (r_name, r_cat, r_tax, r_pr, r_dsc) in enumerate(extra_roots):
        for b_name in brand_pool:
            for p_sz, p_mlt in PACK_SIZES:
                if len(all_products) >= 6500:
                    break
                full_name = f"{b_name} {r_name} - {p_sz}"
                if full_name not in seen_names:
                    seen_names.add(full_name)
                    inv = random.randint(12, 450)
                    price = round(r_pr * p_mlt * random.uniform(0.92, 1.08), 2)
                    pic = f"{slugify(b_name)}_{slugify(r_name)}_{slugify(p_sz)}.jpg"
                    desc = f"{b_name} presents authentic {r_name.lower()} in {p_sz} packaging. {r_dsc}"
                    all_products.append({
                        "Name of the Product": full_name,
                        "Quantity": p_sz,
                        "Category": r_cat,
                        "Inventory": inv,
                        "Price": f"${price:.2f}",
                        "Product Description": desc,
                        "Picture Name": pic,
                        "isTaxable": r_tax
                    })

print(f"Total products ready for export: {len(all_products)}")

# 3. Write CSV
csv_file_path = "data/spicemart_products_6000.csv"
fieldnames = [
    "Name of the Product",
    "Quantity",
    "Category",
    "Inventory",
    "Price",
    "Product Description",
    "Picture Name",
    "isTaxable"
]

print(f"Writing CSV to {csv_file_path}...")
with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in all_products:
        writer.writerow(row)

# 4. Write Excel (.xlsx)
xlsx_file_path = "data/spicemart_products_6000.xlsx"
print(f"Writing Excel workbook to {xlsx_file_path}...")

wb = Workbook()
ws = wb.active
ws.title = "Products Catalog"

ws.append(fieldnames)

header_fill = PatternFill(start_color="059669", end_color="059669", fill_type="solid") # Emerald
header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
thin_border = Border(
    left=Side(style='thin', color='E5E7EB'),
    right=Side(style='thin', color='E5E7EB'),
    top=Side(style='thin', color='E5E7EB'),
    bottom=Side(style='thin', color='E5E7EB')
)

for col_num, header in enumerate(fieldnames, 1):
    cell = ws.cell(row=1, column=col_num)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center")

for row_idx, prod in enumerate(all_products, 2):
    ws.append([
        prod["Name of the Product"],
        prod["Quantity"],
        prod["Category"],
        prod["Inventory"],
        prod["Price"],
        prod["Product Description"],
        prod["Picture Name"],
        prod["isTaxable"]
    ])
    
    row_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid") if row_idx % 2 == 0 else PatternFill(fill_type=None)
    for col_num in range(1, len(fieldnames) + 1):
        c = ws.cell(row=row_idx, column=col_num)
        c.font = Font(name="Arial", size=10)
        c.border = thin_border
        if row_fill.fill_type:
            c.fill = row_fill
        if col_num in [2, 4, 5, 8]:
            c.alignment = Alignment(horizontal="center", vertical="center")

ws.freeze_panes = "A2"

col_widths = {
    1: 45, # Name of the Product
    2: 16, # Quantity
    3: 30, # Category
    4: 14, # Inventory
    5: 14, # Price
    6: 65, # Product Description
    7: 45, # Picture Name
    8: 14  # isTaxable
}

for col_idx, width in col_widths.items():
    col_letter = get_column_letter(col_idx)
    ws.column_dimensions[col_letter].width = width

wb.save(xlsx_file_path)
print(f"COMPLETE! Generated {len(all_products)} records in {xlsx_file_path} and {csv_file_path}!")
