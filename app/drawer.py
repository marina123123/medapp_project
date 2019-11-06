from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("./app/static/cmss10.ttf", 20)

class Drawer:

    def __init__(self, image_path):
        self.im = Image.open(image_path).convert('RGB')


    def draw(self, objects, c):
        if objects == []:
            return

        draw = ImageDraw.Draw(self.im)

        for object in objects:
            ymax = object['ymax']
            ymin = object['ymin']
            xmax = object['xmax']
            xmin = object['xmin']
            label = object['label']

            draw.line([(xmax, ymin), (xmax, ymax)], fill=c, width=2)
            draw.line([(xmax, ymin), (xmax - 10, ymin)], fill=c, width=2)
            draw.line([(xmax, ymax), (xmax - 10, ymax)], fill=c, width=2)
            draw.text((xmax + 4, ymin + (ymax - ymin) / 2), label, font=font, fill=c)


    def draw_v(self, objects, c):
        if objects == []:
            return

        draw = ImageDraw.Draw(self.im)

        for object in objects:
            ymax = object['ymax']
            ymin = object['ymin']
            xmax = object['xmax']
            xmin = object['xmin']
            label = object['label']

            # draw.line([(xmin, ymin), (xmin, ymax)], fill=c, width=2)
            # draw.line([(xmin, ymin), (xmin + 10, ymin)], fill=c, width=2)
            # draw.line([(xmin, ymax), (xmin + 10, ymax)], fill=c, width=2)

            draw.line([(xmin, ymin), (xmin, ymax)], fill=c, width=2)
            draw.line([(xmin, ymax), (xmax, ymax)], fill=c, width=2)
            draw.line([(xmax, ymax), (xmax, ymin)], fill=c, width=2)
            draw.line([(xmax, ymin), (xmin, ymin)], fill=c, width=2)
            draw.text((xmin - 10, ymin + (ymax - ymin) / 2), label, font=font, fill=c)


    def save_im(self, path_save):
        self.im.save(path_save)


