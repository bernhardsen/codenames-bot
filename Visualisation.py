import math
from PIL import Image, ImageDraw, ImageFont

IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600

BOX_WIDTH = 160
BOX_HEIGHT = 120
BOX_MARGINS = 30  # 10px border + 5px padding on each side

FONT_FILE_NAME = './Londrina_Solid/LondrinaSolid-Regular.ttf'
DEFAULT_TEXT_SIZE = 40


class Visualizer:
    def __init__(self):
        self.neutral_bg = Image.open('images/bg/neutral.png').resize((BOX_WIDTH, BOX_HEIGHT), Image.BICUBIC)
        self.neutral_marked_bg = Image.open('images/bg/neutral_marked.png').resize((BOX_WIDTH, BOX_HEIGHT), Image.BICUBIC)
        self.team_1_bg = Image.open('images/bg/team_1.png').resize((BOX_WIDTH, BOX_HEIGHT), Image.BICUBIC)
        self.team_1_marked_bg = Image.open('images/bg/team_1_marked.png').resize((BOX_WIDTH, BOX_HEIGHT), Image.BICUBIC)
        self.team_2_bg = Image.open('images/bg/team_2.png').resize((BOX_WIDTH, BOX_HEIGHT), Image.BICUBIC)
        self.team_2_marked_bg = Image.open('images/bg/team_2_marked.png').resize((BOX_WIDTH, BOX_HEIGHT), Image.BICUBIC)
        self.poison_bg = Image.open('images/bg/poison.png').resize((BOX_WIDTH, BOX_HEIGHT), Image.BICUBIC)
        self.poison_marked_bg = Image.open('images/bg/poison_marked.png').resize((BOX_WIDTH, BOX_HEIGHT), Image.BICUBIC)

    def draw(self, game_state, revealed, filename):
        img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
        context = ImageDraw.Draw(img)
        for i in range(25):
            word = game_state.get_word(i)
            self.draw_word_box(img, context, i, word.word, word.owner, word.marked, revealed)

        del context
        img.save(filename)

    def draw_word_box(self, img, context, position, word, owner, marked, revealed):
        row = math.floor(position / 5)
        column = position % 5

        offset_x = column * BOX_WIDTH
        offset_y = row * BOX_HEIGHT

        bg = self.get_background_image(revealed, owner, marked)
        img.paste(bg, (offset_x, offset_y))

        # Draw the text
        font = ImageFont.truetype(FONT_FILE_NAME, DEFAULT_TEXT_SIZE)
        txt_size = context.textsize(word, font)
        max_text_width = BOX_WIDTH - BOX_MARGINS
        font_size = DEFAULT_TEXT_SIZE
        if txt_size[0] > max_text_width:
            new_font_size = max_text_width / txt_size[0] * DEFAULT_TEXT_SIZE
            font = ImageFont.truetype(FONT_FILE_NAME, round(new_font_size))
            font_size = new_font_size
            x_pos = 0
        else:
            x_pos = (max_text_width - txt_size[0]) / 2
        y_pos = BOX_HEIGHT / 2 - font_size / 2
        context.text((x_pos + offset_x + (BOX_MARGINS / 2), y_pos + offset_y), word, font=font, fill="black")

    def get_background_image(self, alchemist, owner, marked):
        if not alchemist and not marked:
            return self.neutral_bg
        elif owner == 0:
            return self.neutral_marked_bg
        elif owner == 1:
            return self.team_1_marked_bg if marked else self.team_1_bg
        elif owner == 2:
            return self.team_2_marked_bg if marked else self.team_2_bg
        elif owner == 3:
            return self.poison_marked_bg if marked else self.poison_bg

    def draw_team(self, context):
        # Draw team information
        pass
