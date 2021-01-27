from matplotlib import pyplot as plt
import matplotlib.patches as patches


class RectBuilder:
    """ Allows a user to draw a rectangle on a matplotlib plot

    Examples:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        rect = patches.Rectangle((0,0),10,10, edgecolor='b', facecolor='r', alpha=0.3)
        ax.add_patch(rect)
        rectbuilder = RectBuilder(rect)
        rectbuilder.connect()

        The rectangle properties can be retrieved with the Rectangle functions
        rect.get_x(), get_y(), get_width(), get_height()
 
        or the get_bounds() function in this class
        rectbuilder.get_bounds()

    Attributes:
        rect (obj): reference to the matplotlib rectangle patch object
    """
    def __init__(self, rect):
        self.rect = rect
        self.press = False

    def connect(self):
        """Connect to mouse events from user"""
        self.cidpress = self.rect.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.rect.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.rect.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

    def on_press(self, event):
        """ When the mouse is pressed down, define the lower left corner
        of the rectangle """
        if event.inaxes != self.rect.axes: return
        self.press = True
        self.rect.set_bounds(event.xdata, event.ydata, 1, 1)
        self.rect.figure.canvas.draw()

    def on_release(self, event):
        """ When the mouse is pressed down, define the lower left corner
        of the rectangle """
        if event.inaxes != self.rect.axes: return
        self.press = False
        self.rect.set_bounds(self.rect.get_x(), self.rect.get_y(),
                             event.xdata - self.rect.get_x(),
                             event.ydata - self.rect.get_y())
        self.rect.figure.canvas.draw()

    def on_motion(self, event):
        """ When the mouse is pressed down, define the lower left corner
        of the rectangle """
        if event.inaxes != self.rect.axes: return
        if not(self.press): return
        self.rect.set_bounds(self.rect.get_x(), self.rect.get_y(),
                             event.xdata - self.rect.get_x(),
                             event.ydata - self.rect.get_y())
        self.rect.figure.canvas.draw()

    def get_bounds(self):
        """ Returns  xmin, xmax, ymin, ymax """
        x1 = self.rect.get_x()
        x2 = x1 + self.rect.get_width()
        y1 = self.rect.get_y()
        y2 = y1 + self.rect.get_height()
        return min((x1,x2)), max((x1, x2)), min((y1, y2)), max((y1, y2))


# Sample code if run from command line
if __name__ == '__main__':
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rect = patches.Rectangle((0,0),10,10, edgecolor='b', facecolor='r', alpha=0.3)
    ax.add_patch(rect)
    rectbuilder = RectBuilder(rect)
    rectbuilder.connect()

    plt.show()
    print('x: {}, y: {}, maxx {}, ymax {}'.format(
        rect.get_x(), rect.get_y(), rect.get_width(), rect.get_height()))
    print(rectbuilder.get_bounds())
