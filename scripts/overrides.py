# -*- coding: utf-8 -*-
"""Handkorrekturen fuer den Altbestand.

RTGS_B: Umschrift fuer die 82 Eintraege des zweiten Schemas, die gar keine hatten.
POS_OVERRIDE: Wortarten, die sich nicht zuverlaessig aus der deutschen
Uebersetzung ableiten lassen.
GLOSS_FIX / NOTE: inhaltliche Korrekturen und Warnhinweise.
"""

RTGS_B = {
    "ข้างล่าง": "khang lang", "แมว": "maeo", "บน": "bon", "แพทย์": "phaet",
    "ซื้อ": "sue", "ประตู": "pratu", "ข้างหน้า": "khang na", "ร้อน": "ron",
    "นัดหมาย": "nat mai", "เครื่องบิน": "khrueang bin", "Wi-Fi": "wai-fai",
    "หิว": "hio", "เปียก": "piak", "เลย": "loei", "นักดนตรี": "nak dontri",
    "ลูกสาว": "luk sao", "สีเขียว": "si khiao", "ข้าวผัด": "khao phat",
    "รองเท้า": "rongthao", "วันอาทิตย์": "wan athit", "เช็คอิน": "chek-in",
    "ปลา": "pla", "ตรงข้าม": "trong kham", "กรกฎาคม": "karakadakhom",
    "แห้ง": "haeng", "กับ": "kap", "ปีนเขา": "pin khao", "นักเรียน": "nakrian",
    "ฤดูฝน": "ruedu fon", "หิมะ": "hima", "แดด": "daet", "ใหม่": "mai",
    "รหัสผ่าน": "rahat phan", "ดินสอ": "dinso", "วันอังคาร": "wan angkhan",
    "ลูก": "luk", "ธันวาคม": "thanwakhom", "ใช้": "chai", "สีดำ": "si dam",
    "ช่างภาพ": "chang phap", "ฝน": "fon", "เท้า": "thao",
    "วันพฤหัสบดี": "wan pharuehatsabodi", "สตรอว์เบอร์รี": "satroboeri",
    "พบ": "phop", "หมวก": "muak", "ที่พัก": "thi phak", "พายุ": "phayu",
    "พี่สาว": "phi sao", "ตำรวจ": "tamruat", "กระโปรง": "kraprong",
    "อินเทอร์เน็ต": "inthoenet", "มันฝรั่ง": "man farang",
    "แกงเขียวหวาน": "kaeng khiao wan", "มือ": "mue", "คืน": "khuen",
    "เก้าอี้": "kao-i", "เจ็บ": "chep", "กะหล่ำปลี": "kalam pli",
    "ตะวันออก": "tawan ok", "ส่วนลด": "suan lot", "สิงหาคม": "singhakhom",
    "ห้องครัว": "hong khrua", "พ่อ": "pho", "รูปภาพ": "rup phap",
    "ภูเขา": "phukhao", "เงินทอน": "ngoen thon", "สิ": "si",
    "มอเตอร์ไซค์": "motoesai", "ทดลอง": "thotlong", "กุญแจ": "kunchae",
    "ถาม": "tham", "วัด": "wat", "ห้างสรรพสินค้า": "hang sapphasinkha",
    "มีนาคม": "minakhom", "หัว": "hua", "การบ้าน": "kan ban",
    "พฤศจิกายน": "phruetsachikayon", "ถ่ายรูป": "thai rup",
    "คู่มือท่องเที่ยว": "khumue thongthiao", "ทะเลทราย": "thale sai", "อา": "a",
}

# Umschriften im Altbestand, die klar von RTGS abweichen
RTGS_FIX = {
    "สวัสดี": "sawatdi",              # -ส im Silbenauslaut ist -t
    "วันจันทร์": "wan chan",           # RTGS kennt kein "j"
    "วันพฤหัสบดี": "wan pharuehatsabodi",  # war abgeschnitten
    "งานอดิเรก": "ngan adirek",
    "ปลอดภัย": "plot phai",           # -ด im Auslaut ist -t
    "ฤดูฝน": "ruedu fon", "ฤดูหนาว": "ruedu nao", "ฤดูร้อน": "ruedu ron",  # ฤ = rue
    "รถเมล์": "rot me",
    "หิว": "hio",                     # -ิว = -io
    "เก้าอี้": "kao-i",
    "หนังสือ": "nangsue",
    "ซูเปอร์มาร์เก็ต": "supoemaket",
}

POS_OVERRIDE = {
    "สวัสดี": "Interjektion", "ขอบคุณ": "Interjektion/Verb",
    "ขอโทษ": "Interjektion/Verb", "ได้โปรด": "Adverb",
    "ใช่": "Verb/Partikel", "ไม่": "Partikel", "กรุณา": "Adverb/Verb",
    "ถึง": "Verb/Praeposition", "ออก": "Verb/Adverb", "เข้า": "Verb/Adverb",
    "ผัด": "Verb/Nomen", "พี่": "Nomen", "น้อง": "Nomen",
    "เมื่อวาน": "Adverb/Nomen", "วันนี้": "Adverb/Nomen",
    "พรุ่งนี้": "Adverb/Nomen", "เช้า": "Nomen/Adjektiv",
    "เย็น": "Nomen/Adjektiv", "คืน": "Nomen/Verb", "ถึงเวลา": "Phrase",
    "เปิดบัญชี": "Verbphrase", "ถอนเงิน": "Verbphrase", "โอนเงิน": "Verbphrase",
    "ราคาเท่าไหร่": "Phrase", "ลดราคา": "Verb/Nomen",
    "ใบเสร็จรับเงิน": "Nomen", "ช่วยด้วย": "Interjektion",
    "ระวัง": "Verb/Interjektion", "ข้างหลัง": "Adverb/Praeposition",
    "ล่าง": "Adjektiv/Adverb", "ใน": "Praeposition",
    "นอก": "Praeposition/Adverb", "บน": "Praeposition/Adverb",
    "ข้างหน้า": "Adverb/Praeposition", "ซ้าย": "Nomen/Adverb",
    "ขวา": "Nomen/Adverb", "ตรง": "Adverb/Verb", "แยก": "Nomen/Verb",
    "เล็ก": "Adjektiv", "เขียว": "Adjektiv", "ไทย": "Nomen/Adjektiv",
    "อังกฤษ": "Nomen/Adjektiv", "เยอรมัน": "Nomen/Adjektiv",
    "ตา": "Nomen", "ปาก": "Nomen", "หู": "Nomen",
}

# Inhaltliche Korrekturen an Uebersetzung/Schreibweise
GLOSS_FIX = {
    "ซุปเปอร์มาร์เก็ต": {"thai": "ซูเปอร์มาร์เก็ต", "forvo_slug": "ซูเปอร์มาร์เก็ต"},
}

NOTES = {
    "ชัง": "Literarisch/gehoben. Im Alltag sagt man เกลียด (kliat).",
    "ได้โปรด": "Sehr formell/schriftsprachlich. Im Alltag: กรุณา oder ...หน่อย.",
    "ซูเปอร์มาร์เก็ต": "Schreibweise nach Royal Institute; ซุปเปอร์... ist umgangssprachlich verbreitet.",
    "หมา": "Umgangssprachlich; neutral/hoeflich ist สุนัข (sunak).",
    "น้ำเงิน": "Als Farbbezeichnung meist สีน้ำเงิน; bezeichnet Dunkelblau.",
    "Wi-Fi": "Lateinische Schreibung; im Thai auch ไวไฟ. Keine Tonanalyse moeglich.",
}
