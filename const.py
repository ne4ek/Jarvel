import os

MAX_MESSAGES = 50

# Word list for generating random companies' codes
WORD_LIST = [
    "Calm",
    "Bright",
    "Laughing",
    "Bliss",
    "Velvet",
    "Melody",
    "Ruby",
    "Night",
    "Symphony",
    "Infinity",
    "Sunshine",
    "Forest",
    "Jade",
    "Crystal",
    "Radiance",
    "Tranquil",
    "Happy",
    "Mystic",
    "Joy",
    "Dawn",
    "Mind",
    "Purity",
    "Dusk",
    "Sunrise",
    "Topaz",
    "Lagoon",
    "Mountain",
    "Journey",
    "Twilight",
    "Harmony",
    "Peaceful",
    "Memories",
    "Peak",
    "Serene",
    "Wave",
    "Majestic",
    "Meadow",
    "Cerulean",
    "Echo",
    "Zen",
    "Diamond",
    "Verdant",
    "Dream",
    "Soul",
    "Cascading",
    "Solitude",
    "Amethyst",
    "Vibrant",
    "Pearl",
    "Pond",
    "Lavender",
    "Radiant",
    "Flow",
    "Serenity",
    "Rainbow",
    "Ethereal",
    "Grove",
    "Breeze",
    "Silk",
    "Galaxy",
    "Whisper",
    "Sapphire",
    "Crimson",
    "Opal",
    "Gentle",
    "Luminous",
    "Golden",
    "Amber",
    "Cosmic",
    "Sky",
    "Eternal",
    "River",
    "Universe",
    "Sunset",
    "Ocean",
    "Star",
    "Blossom",
    "Azure",
    "Emerald",
    "Day",
    "Field",
]

CTRL_MESSAGES = [
    "Какой статус?",
    "Какой статус у задачи?",
    "Как дела с этим?",
    "Как дела?",
    "Апаю",
]

BOT_MENTIONS = ["джарвел", "ягодка"]

DIRNAME = os.path.dirname(__file__)

VOICE_WORDS = "ИИЗам, chatGPT, апатель, КТРЛ, FYI, Румата, Джарвел"

ARCHIVE_TASK_STATUSES = ["complete", "cancelled"]
PERSONAL_TASK_STATUSES = ["active", "pending"]
ORDER_STATUSES = ["active", "overdue", "pending"]
TASK_STATUSES = ["active", "overdue"]   


ALL_MEETINGS_LIST_STATUSES = ["pending", "cancelled", "complete"]
