import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('Backend-motos/.env')

def seed_ultimate_inventory():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        cur = conn.cursor()
        print("INFO: Iniciando carga DEFINITIVA de inventario (AKT, Auteco, Global)...")

        # Clear existing parts to avoid duplicates
        cur.execute("DELETE FROM part;")

        # Structure: Brand -> Models with Year Ranges
        brands_models_years = {
            "AKT": [
                ("NKD 125", "2010-2025"), ("TTR 200", "2015-2025"),
                ("CR4 125/165", "2017-2024"), ("Special 110", "2010-2024"),
                ("Dynamic Pro 125", "2012-2024"), ("RTX 150", "2014-2020"),
                ("TT Dual Sport 180", "2018-2025")
            ],
            "Pulsar (Auteco)": [
                ("NS 200 / FI", "2012-2025"), ("NS 160", "2017-2024"),
                ("220F / Neon", "2009-2023"), ("180 UG", "2001-2022"),
                ("N250 / F250", "2023-2026"), ("RS 200", "2015-2024")
            ],
            "Platino (Auteco)": [
                ("Platino 100 / 110", "2000-2025"), ("Platino 125", "2005-2020")
            ],
            "Boxer (Auteco)": [
                ("CT 100 ES/KS", "2000-2025"), ("BM 150", "2010-2024"),
                ("CT 125", "2022-2025"), ("S (Slim)", "2015-2024")
            ],
            "TVS (Auteco/HM)": [
                ("Apache RTR 160 4V", "2018-2025"), ("Apache RTR 200 4V", "2016-2025"),
                ("Raider 125", "2021-2026"), ("Ntorq 125", "2018-2025"),
                ("Sport 100", "2010-2024"), ("Apache RR 310", "2018-2024")
            ],
            "KTM (Auteco)": [
                ("Duke 200/250/390", "2012-2025"), ("RC 200/390", "2014-2024"),
                ("Adventure 250/390", "2020-2026"), ("Duke 790/890", "2018-2025"),
                ("1290 Super Adventure", "2015-2024")
            ],
            "Kawasaki (Auteco)": [
                ("Ninja 300/400", "2013-2025"), ("Versys X-300", "2017-2024"),
                ("Z400 / Z900", "2019-2025"), ("KLR 650 (New Gen)", "2022-2026")
            ],
            "Honda": [
                ("CB 190R", "2016-2025"), ("XR 150L / 190L", "2014-2025"),
                ("XRE 300 / Sahara", "2010-2026"), ("CB 125F / Twister", "2015-2024"),
                ("Africa Twin 1100", "2020-2025"), ("CBR 600 RR", "2003-2024")
            ],
            "Yamaha": [
                ("FZ 25 / FZ 2.0", "2010-2025"), ("MT-03 / MT-07 / MT-09", "2014-2025"),
                ("NMAX 155", "2015-2025"), ("XTZ 125 / 150 / 250", "2005-2026"),
                ("Crypton FI", "2012-2024"), ("YZF-R15 V3/V4", "2017-2025")
            ],
            "Suzuki": [
                ("Gixxer 150/250", "2015-2025"), ("V-Strom 250/650/1050", "2004-2026"),
                ("GN 125", "2000-2025"), ("DR 650 SE", "2000-2025"),
                ("AX4 / AX100", "2000-2024"), ("GSX-S 750 / 1000", "2015-2024")
            ],
            "Kymco": [
                ("Agility City / Digital", "2008-2025"), ("Downtown 300/350", "2010-2024"),
                ("AK 550", "2017-2024"), ("Like 125/150", "2012-2024")
            ],
            "BMW": [
                ("G 310 R / GS", "2017-2025"), ("F 850 GS / 900 GS", "2018-2026"),
                ("R 1250 GS Adventure", "2019-2024"), ("S 1000 RR", "2009-2025")
            ],
            "Ducati": [
                ("Monster 937", "2021-2025"), ("Multistrada V4", "2021-2025"),
                ("Scrambler 800", "2015-2024")
            ]
        }
        
        # Parts specialized by Category
        parts_catalog = {
            "Motor & Performance": [
                ("Filtro de Aceite (Elemento)", 18000, 50),
                ("Filtro de Aceite (Metálico)", 35000, 30),
                ("Filtro de Aire Original", 45000, 25),
                ("Bujía NGK Standard", 12000, 100),
                ("Bujía Iridium NGK", 55000, 40),
                ("Kit de Cilindro Completo", 350000, 5),
                ("Juego de Valvulas", 65000, 15),
                ("Cárter / Empaque Tapa", 12000, 30),
                ("Bomba de Aceite", 85000, 10)
            ],
            "Transmisión": [
                ("Kit Arrastre Acero 1045", 145000, 15),
                ("Kit Arrastre Reforzado O-Ring", 285000, 10),
                ("Cadena 428/520/525", 85000, 20),
                ("Discos de Clutch (Set)", 75000, 20),
                ("Piñón de Salida Aligerado", 25000, 15),
                ("Rulemán de Rueda", 15000, 40)
            ],
            "Frenos": [
                ("Pastillas Delanteras (Semimetálicas)", 35000, 40),
                ("Pastillas Traseras (Sinterizadas)", 55000, 30),
                ("Bandas de Freno", 28000, 30),
                ("Disco de Freno Delantero", 185000, 10),
                ("Líquido de Frenos DOT 4", 15000, 50),
                ("Kit Reparación Mordaza", 32000, 15)
            ],
            "Suspensión & Chasis": [
                ("Retenes de Telescópico (Par)", 45000, 25),
                ("Aceite de Suspensión (1/4)", 35000, 20),
                ("Amortiguador Trasero (Monoshock)", 450000, 5),
                ("Cunas de Dirección (Kit)", 65000, 15),
                ("Bujes de Tijera", 28000, 20)
            ],
            "Eléctrico": [
                ("Batería Seca 12V 7Ah/9Ah", 135000, 15),
                ("Batería Gel Sellada", 165000, 12),
                ("Bombillo Faro LED (H4/M5)", 45000, 25),
                ("Regulador de Voltaje", 85000, 10),
                ("Relé de Arranque", 25000, 20),
                ("Estator / Bobina", 145000, 8),
                ("CDI / ECU Control", 250000, 5)
            ],
            "Estética & Accesorios": [
                ("Espejos Originales (Par)", 55000, 20),
                ("Manigueta Freno/Clutch", 18000, 30),
                ("Puños / Manillares Comfort", 25000, 25),
                ("Guaya de Clutch / Acelerador", 12000, 40),
                ("Defensa de Motor / Sliders", 185000, 8),
                ("Posa Pies Goma", 15000, 20)
            ]
        }

        parts_to_insert = []
        for brand, models_meta in brands_models_years.items():
            for model_name, years in models_meta:
                # Brand segment multiplier
                segment_multiplier = 1.0
                if brand in ["BMW", "Ducati", "KTM (Auteco)"]: segment_multiplier = 2.8
                elif brand in ["Kawasaki (Auteco)", "Yamaha", "Honda", "Suzuki"]: segment_multiplier = 1.8
                elif brand in ["TVS (Auteco/HM)", "Kymco", "Pulsar (Auteco)"]: segment_multiplier = 1.3
                else: segment_multiplier = 0.9 # AKT, Boxer
                
                # Model complexity multiplier
                model_multiplier = 1.0
                if any(x in model_name for x in ["1000", "GS", "R1", "V4", "1290", "900", "800"]):
                    model_multiplier = 2.0
                elif any(x in model_name for x in ["200", "250", "300", "400"]):
                    model_multiplier = 1.3
                
                for category, items in parts_catalog.items():
                    for part_name_base, base_price, stock in items:
                        final_price = int(base_price * segment_multiplier * model_multiplier)
                        # Structured naming
                        full_model = f"{model_name} [{years}]"
                        final_name = f"{part_name_base} - {model_name}"
                        
                        parts_to_insert.append((final_name, brand, full_model, final_price, stock, category))

        print(f"INFO: Generando {len(parts_to_insert)} referencias MAESTRAS definitivas...")
        
        cur.executemany("""
            INSERT INTO part (name, brand, model, price, stock, category) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, parts_to_insert)

        conn.commit()
        print(f"SUCCESS: {len(parts_to_insert)} repuestos organizados y cargados exitosamente.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    seed_ultimate_inventory()
