# -*- coding: utf-8 -*-
"""Themenzuordnung fuer den Bestand aus words.json (Stand vor der Bereinigung).

Die Schema-A-Eintraege (Index 0-232) lagen bereits in einer Lehrplan-Reihenfolge
vor; daraus ergeben sich die Bereiche. Schema-B-Eintraege werden einzeln zugeordnet.
"""

TOPIC_RANGES = [
    (0, 6, "Begruessung & Hoeflichkeit"),
    (7, 11, "Bewegung"),
    (12, 13, "Essen & Trinken"),
    (14, 25, "Einkaufen & Geld"),
    (26, 44, "Essen & Trinken"),
    (45, 61, "Wohnen & Haushalt"),
    (62, 74, "Familie & Menschen"),
    (75, 80, "Schule & Lernen"),
    (81, 90, "Zeit & Kalender"),
    (91, 99, "Zeit & Kalender"),
    (100, 108, "Wetter & Jahreszeiten"),
    (109, 116, "Reisen & Verkehr"),
    (117, 117, "Zeit & Kalender"),
    (118, 122, "Reisen & Verkehr"),
    (123, 128, "Freizeit & Medien"),
    (129, 136, "Arbeit & Beruf"),
    (137, 151, "Gesundheit & Koerper"),
    (152, 164, "Gefuehle & Kommunikation"),
    (165, 172, "Einkaufen & Geld"),
    (173, 175, "Notfall & Sicherheit"),
    (176, 182, "Schule & Lernen"),
    (183, 188, "Eigenschaften"),
    (189, 200, "Richtung & Ort"),
    (201, 211, "Eigenschaften"),
    (212, 219, "Natur & Orte"),
    (220, 223, "Sprachen & Laender"),
    (224, 232, "Farben"),
]

TOPIC_BY_WORD = {
    "ข้างล่าง": "Richtung & Ort", "แมว": "Tiere", "บน": "Richtung & Ort",
    "แพทย์": "Gesundheit & Koerper", "ซื้อ": "Einkaufen & Geld",
    "ประตู": "Wohnen & Haushalt", "ข้างหน้า": "Richtung & Ort",
    "ร้อน": "Wetter & Jahreszeiten", "นัดหมาย": "Arbeit & Beruf",
    "เครื่องบิน": "Reisen & Verkehr", "Wi-Fi": "Technik & Internet",
    "หิว": "Essen & Trinken", "เปียก": "Eigenschaften",
    "เลย": "Grammatik & Partikeln", "นักดนตรี": "Arbeit & Beruf",
    "ลูกสาว": "Familie & Menschen", "สีเขียว": "Farben",
    "ข้าวผัด": "Essen & Trinken", "รองเท้า": "Kleidung",
    "วันอาทิตย์": "Zeit & Kalender", "เช็คอิน": "Reisen & Verkehr",
    "ปลา": "Essen & Trinken", "ตรงข้าม": "Richtung & Ort",
    "กรกฎาคม": "Zeit & Kalender", "แห้ง": "Eigenschaften",
    "กับ": "Grammatik & Partikeln", "ปีนเขา": "Freizeit & Medien",
    "นักเรียน": "Schule & Lernen", "ฤดูฝน": "Wetter & Jahreszeiten",
    "หิมะ": "Wetter & Jahreszeiten", "แดด": "Wetter & Jahreszeiten",
    "ใหม่": "Eigenschaften", "รหัสผ่าน": "Technik & Internet",
    "ดินสอ": "Schule & Lernen", "วันอังคาร": "Zeit & Kalender",
    "ลูก": "Familie & Menschen", "ธันวาคม": "Zeit & Kalender",
    "ใช้": "Alltagsverben", "สีดำ": "Farben", "ช่างภาพ": "Arbeit & Beruf",
    "ฝน": "Wetter & Jahreszeiten", "เท้า": "Gesundheit & Koerper",
    "วันพฤหัสบดี": "Zeit & Kalender", "สตรอว์เบอร์รี": "Essen & Trinken",
    "พบ": "Alltagsverben", "หมวก": "Kleidung", "ที่พัก": "Reisen & Verkehr",
    "พายุ": "Wetter & Jahreszeiten", "พี่สาว": "Familie & Menschen",
    "ตำรวจ": "Notfall & Sicherheit", "กระโปรง": "Kleidung",
    "อินเทอร์เน็ต": "Technik & Internet", "มันฝรั่ง": "Essen & Trinken",
    "แกงเขียวหวาน": "Essen & Trinken", "มือ": "Gesundheit & Koerper",
    "คืน": "Alltagsverben", "เก้าอี้": "Wohnen & Haushalt",
    "เจ็บ": "Gesundheit & Koerper", "กะหล่ำปลี": "Essen & Trinken",
    "ตะวันออก": "Richtung & Ort", "ส่วนลด": "Einkaufen & Geld",
    "สิงหาคม": "Zeit & Kalender", "ห้องครัว": "Wohnen & Haushalt",
    "พ่อ": "Familie & Menschen", "รูปภาพ": "Freizeit & Medien",
    "ภูเขา": "Natur & Orte", "เงินทอน": "Einkaufen & Geld",
    "สิ": "Grammatik & Partikeln", "มอเตอร์ไซค์": "Reisen & Verkehr",
    "ทดลอง": "Alltagsverben", "กุญแจ": "Wohnen & Haushalt",
    "ถาม": "Gefuehle & Kommunikation", "วัด": "Natur & Orte",
    "ห้างสรรพสินค้า": "Einkaufen & Geld", "มีนาคม": "Zeit & Kalender",
    "หัว": "Gesundheit & Koerper", "การบ้าน": "Schule & Lernen",
    "พฤศจิกายน": "Zeit & Kalender", "ถ่ายรูป": "Freizeit & Medien",
    "คู่มือท่องเที่ยว": "Reisen & Verkehr", "ทะเลทราย": "Natur & Orte",
    "อา": "Familie & Menschen",
}


def topic_for(index, word):
    for lo, hi, name in TOPIC_RANGES:
        if lo <= index <= hi:
            return name
    return TOPIC_BY_WORD.get(word)
