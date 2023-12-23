import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import numpy as np

data = np.random.randint(0, 301, size=(8, 50)).tolist()


class DataWaveformViewer:
    isPlaying = False

    def __init__(self, time, data):
        self.time = time
        self.data = data
        self.fig, self.axes = plt.subplots(4, 2, figsize=(10, 6))
        self.fig.suptitle('Data Waveforms')
        self.lines = []
        self.length = len(time)
        # self.ax.plot(self.time, self.data)
        # self.ax.set_xlabel('Time')
        # self.ax.set_ylabel('Data')
        # self.ax.set_title('Data Waveform')

        for idx, ax in enumerate(self.axes.flatten()):
            if idx < 8:
                line, = ax.plot(time, data[idx])
                ax.set_xlim(0, 5)
                ax.set_xlabel('Time')
                ax.set_ylabel('Data Source {}'.format(idx + 1))
                ax.set_title('Data Source {}'.format(idx + 1))
                self.lines.append(line)
            else:
                ax.axis('off')
        self.dragging = False
        self.start_x = None

        self.fig.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_button_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion_notify)

        self.fig.tight_layout()

        self.button_ax = plt.axes([0.7, 0.05, 0.1, 0.075])
        self.button = Button(self.button_ax, 'Play')
        self.button.on_clicked(self.play_animation)
        self.ani = animation.FuncAnimation(self.fig, self.update, frames=len(time), interval=27, blit=True)

    def play_animation(self, event):
        if self.isPlaying:
            self.ani.event_source.stop()
            self.button.label.set_text('Play')
            self.isPlaying = False
        else:
            self.ani.event_source.start()
            self.button.label.set_text('Stop')
            self.isPlaying = True

    def update(self, frame):
        if self.isPlaying and frame < len(self.time):
            # 计算波形数据的显示范围
            start_idx = max(0, frame - len(time) + 1)
            end_idx = frame + 1
            # line.set_data(time[start_idx:end_idx], data[start_idx:end_idx])

            # 设置X轴显示范围，实现向左移动效果
            # ax.set_xlim(frame - len(time) + 1, frame + 1)
            for i, ax in enumerate(self.axes.flatten()):
                # ax.set_xlim(ax.get_xlim()[0] - 1, ax.get_xlim()[1] - 1)
                if frame <= 5:
                    self.lines[i].set_data(time[:frame], self.data[i][:frame])
                else:
                    self.lines[i].set_data(time[frame - 5:frame], self.data[i][frame - 5:frame])
                ax.set_xlim(time[frame] - 3, time[frame] + 2)
            self.fig.canvas.draw()
        else:
            # pass
            self.ani.event_source.stop()
            self.button.label.set_text('Play')
            self.isPlaying = False
        return self.lines


    def on_button_press(self, event):
        if event.button == 1:  # 左键按下
            self.dragging = True
            self.start_x = event.xdata

    def on_button_release(self, event):
        if event.button == 1:  # 左键释放
            self.dragging = False
            self.start_x = None

    def on_motion_notify(self, event):
        if self.dragging:
            if self.start_x is not None and event.xdata is not None:
                print("moving")
                # dx = event.xdata - self.start_x
                # for i, ax in enumerate(self.axes.flatten()):
                #     # print(f"xlim[0] {ax.get_xlim()[0]} xlim[1] {ax.get_xlim()[1]}")
                #     ax.set_xlim(ax.get_xlim()[0] - dx, ax.get_xlim()[1] - dx)
                # self.fig.canvas.draw()


time = np.arange(0, 50).tolist()


viewer = DataWaveformViewer(time, data)

plt.show()
