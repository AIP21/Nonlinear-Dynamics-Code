package Programs;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.Function;

import javax.swing.JFrame;
import javax.swing.SwingUtilities;
import javax.swing.event.MouseInputListener;
import javax.swing.JPanel;

import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.event.MouseEvent;
import java.awt.image.BufferedImage;
import java.awt.geom.Point2D;

public class NonlinearVisualizer2 extends JFrame implements MouseInputListener {
    // region Options
    // region Functions
    private final Function<Float, Float> custom = (in) -> {
        // if (in % 10 == 0)
        // return in % 2;
        // else
        // return in ^ 2;

        // return in / ((in % 50) == 0 ? 2 : in % 50);

        // return (int) (-Math.signum(in) * Math.sqrt(Math.abs(in)));

        // return (in % 5 == in) ? in % 10 : in % 2;

        // return (1f - in) / (3f * in + 1f);

        return ((3f * in) + 2) / ((2f * in) + 1);
    };

    private final Function<Float, Float> collatz = (in) -> {
        if (in % 2 == 0)
            return in / 2f;
        else
            return (in * 3f + 1f) / 2f; // optimized by dividing by two
    };

    private final Function<Float, Float> collatzFractal = (in) -> {
        return (float) (0.5 * in * Math.acos((Math.PI / 2f) * in)
                + (((3f * in) + 1f) / 2f) * Math.asin((Math.PI / 2f) * in));
        // ???
    };

    private final Function<Float, Float> iwanski = (in) -> {
        float n = in;
        int sum = 0;
        while (n > 0) {
            float d = n / 10;
            float k = n % 10;
            n = d;
            sum += k * k;
        }
        return (float) sum;
    };

    private final Function<Float, Float> rand = (in) -> {
        return (float) Math.random() * 10f;
    };

    private final Function<Float, Float> cosine = (in) -> {
        return (float) Math.cos(in / 10f) * 10f;
    };

    private final Function<Float, Float> sine = (in) -> {
        return (float) Math.sin(in / 10f) * 10f;
    };

    private final Function<Float, Float> add = (in) -> {
        return in + 1f;
    };

    private final Function<Float, Float> randWalk = (in) -> {
        return (float) (in + (Math.random() - 0.5f) * 10f);
    };
    // endregion

    private boolean automatic = false; // Whether or not to automatically iterate
    private boolean statusColors = false; // Whether or not to color pixels by their status (zero, one, cycle, or
    private boolean tripLengthColor = false; // Whether or not to color pixels by their trip length (true) or by their
                                             // value (false)
    private int maxIterations = 0; // The maximum number of times to iterate when using automatic

    private int width = 852, height = 480; // The size of the screen to render (default 852, 480)
    private int itersPerSecond = 30; // The amount of iterations to execute per second (the fps) (default 30)

    private int THREAD_COUNT = 4; // The number of threads to use for multithreading computation
    // endregion

    // region Variables
    private Runner runner;
    private DrawPanel panel;

    private Function<Float, Float> selectedFunction = collatz;
    private String selectedFuncName = "";

    private Pixel2D[] pixels; // The values for every pixel

    private float curMax = Float.MIN_VALUE, curMin = Float.MAX_VALUE, curMaxTrip = Float.MIN_VALUE;
    private int iteration;
    private boolean doneIterating = false;
    private boolean paused = false;
    private boolean finishedProcessing;

    private Point2D pixelPos;

    private int runningThreads;

    private final Font font = new Font("Arial", Font.PLAIN, 12);
    private final Color labelBackgroundColor = new Color(184, 184, 184, 200);
    private final Color labelTextColor = Color.black;

    private final Color minColor = new Color(0, 76, 109); // 38, 0, 5
    private final Color maxColor = new Color(193, 231, 255); // 190, 28, 109
    private final Color minDoneColor = new Color(38, 100, 5);
    private final Color maxDoneColor = new Color(190, 128, 109);
    private final Color minCycleColor = new Color(38, 0, 105);
    private final Color maxCycleColor = new Color(190, 28, 209);

    private boolean shouldRebuildImage = true;

    // Main thread timings
    private ArrayList<Float> timings = new ArrayList<>();
    private float averageTime;

    // Pixel2D worker thread timings
    private ArrayList<Float> threadTimings = new ArrayList<>();
    private float currentThreadTime;
    private float averageThreadTime;
    // endregion

    public NonlinearVisualizer2(String[] args) {
        getParams(args);

        setVisible(true);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(500, 500);
        setResizable(true);
        setBackground(minColor);

        pixels = new Pixel2D[width * height];

        curMax = pixels.length;
        curMin = 0;

        // TODO: Make it use coordinates instead of index

        for (int i = 0; i < pixels.length; i++) {
            pixels[i] = new Pixel2D(getCoordAtIndex(i));
        }

        // Add the input listeners
        addMouseListener(this);
        addMouseMotionListener(this);

        // Create the automatic runner
        runner = new Runner();
        new Thread(runner).start();

        // Create the draw panel
        panel = new DrawPanel();
        add(panel);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new NonlinearVisualizer2(args);
        });
    }

    // region Input Arguments Stuff
    // Get the inputted parameters from args
    private void getParams(String[] args) {
        for (String arg : args) {
            if (arg.equals("help")) {
                printHelp();
            } else if (arg.equals("auto")) {
                automatic = true;
            } else if (arg.equals("statusColors")) {
                statusColors = true;
            } else if (arg.contains("iters=")) {
                maxIterations = Integer.parseInt(arg.replace("iters=", ""));
            } else if (arg.contains("fps=")) {
                itersPerSecond = Integer.parseInt(arg.replace("fps=", ""));
            } else if (arg.contains("width=")) {
                width = Integer.parseInt(arg.replace("width=", ""));
            } else if (arg.contains("height=")) {
                height = Integer.parseInt(arg.replace("height=", ""));
            } else if (arg.contains("threads=")) {
                THREAD_COUNT = Integer.parseInt(arg.replace("threads=", ""));
            } else if (arg.contains("func=")) {
                getFunctions(arg.replace("func=", ""));
            }
        }
    }

    // Get the possible functions
    private void getFunctions(String func) {
        switch (func) {
            case "collatz":
                selectedFunction = collatz;
                selectedFuncName = "Collatz's Problem";
                break;
            case "collatzFractal":
                selectedFunction = collatzFractal;
                selectedFuncName = "Collatz's Problem (Fractal)";
                break;
            case "iwanski":
                selectedFunction = iwanski;
                selectedFuncName = "Iwanski's Problem";
                break;
            case "rand":
                selectedFunction = rand;
                selectedFuncName = "Random";
                break;
            case "cosine":
                selectedFunction = cosine;
                selectedFuncName = "Cosine";
                break;
            case "sine":
                selectedFunction = sine;
                selectedFuncName = "Sine";
                break;
            case "add":
                selectedFunction = add;
                selectedFuncName = "Add";
                break;
            case "randWalk":
                selectedFunction = randWalk;
                selectedFuncName = "Random Walk";
                break;
            case "custom":
                selectedFunction = custom;
                selectedFuncName = "Custom function";
                break;
        }
    }

    // Print the help info
    private void printHelp() {
        System.out.println("--------HELP--------");
        System.out.println("<help> : Show this page");
        System.out.println("<auto> : Automatically iterate instead of on-click");
        System.out.println(
                "<statusColors> : Color pixels based on their status (one, zero, cycling, or not yet complete)");
        System.out.println(
                "<iters=> : The maximum number of times to iterate when using automatic (0 to disable) (disabled by default)");
        System.out.println("<fps=> : The amount of iterations to execute per second (the fps) (default is 30)");
        System.out.println("<width=> : The width of the draw area (default is 852)");
        System.out.println("<height=> : The height of the draw area (default is 480)");
        System.out.println("<threads=> : The maximum number of threads to use for computing pixels (default is 4)");
        System.out.println(
                "<func=> : The name of the function to use. (collatz, collatzFractal, iwanski, rand, cosine, sine, add, randWalk, custom) (default is collatz)");
        System.out.println("--------------------");
        System.exit(0);
    }
    // endregion

    // The primary function. Iterates over every pixel and applies the selected
    // function to its value.
    private void tick() {
        if (!paused && runningThreads == 0 && !finishedProcessing) {
            new Thread(new Runnable() {
                public void run() {
                    if (!automatic || maxIterations == 0 || iteration < maxIterations) {
                        iteration++;
                        finishedProcessing = true;

                        long st = System.nanoTime();
                        curMax = Float.MIN_VALUE;
                        curMin = Float.MAX_VALUE;

                        // Iterate one step of each pixel (set the pixel to the function's output when
                        // inputted the current pixel value)
                        if (THREAD_COUNT != 1) {
                            int pxSection = (int) Math.ceil((float) pixels.length / (float) THREAD_COUNT);
                            ArrayList<RunThread> threads = new ArrayList<RunThread>();
                            for (int threadNum = 0; threadNum < THREAD_COUNT; threadNum++) {
                                threads.add(new RunThread(threadNum * pxSection, (threadNum + 1) * pxSection));
                            }

                            // runningThreads = THREAD_COUNT;

                            for (RunThread td : threads) {
                                td.start();
                                System.out.println("Started new thread: " + td.getName());
                            }

                            for (RunThread td : threads) {
                                try {
                                    td.join();
                                } catch (Exception e) {
                                    System.out.println(
                                            "Exception or interruption in Pixel2D Worker thread: " + e.getStackTrace());
                                }
                            }
                        } else {
                            Thread td = new RunThread(0, pixels.length);
                            td.start();

                            try {
                                td.join();
                            } catch (Exception e) {
                                System.out.println(
                                        "Exception or interruption in Pixel2D Worker thread: " + e.getStackTrace());
                            }
                        }

                        // Get the timings and average them
                        float time = (System.nanoTime() - st) / 1000000f;
                        if (timings.size() >= 60) {
                            timings.remove(0);
                        }
                        timings.add(time);

                        float sum = 0;
                        for (Float d : timings) {
                            sum += d;
                        }
                        averageTime = sum / timings.size();

                        // Get the thread timings and average them
                        if (threadTimings.size() >= 60) {
                            threadTimings.remove(0);
                        }
                        currentThreadTime /= THREAD_COUNT;
                        threadTimings.add(currentThreadTime);

                        sum = 0;
                        for (Float d : threadTimings) {
                            sum += d;
                        }
                        averageThreadTime = sum / threadTimings.size();

                        shouldRebuildImage = true;

                        System.out.println(String.format(
                                "Iteration #%d took %.3fms", iteration,
                                time + currentThreadTime));
                    } else {
                        doneIterating = true;
                        System.out.println(
                                String.format("Finished iterating! Reached max configured iterations: %d",
                                        maxIterations));
                    }
                }
            }).start();
        } else {
            if (finishedProcessing && !doneIterating) {
                doneIterating = true;
                System.out.println(
                        String.format(
                                "Finished iterating! Every pixel has reached 1 or 0, or is in a cycle. Took %d iterations",
                                iteration));
            }
        }
    }

    // region Inner Classes
    private class Pixel2D {
        protected Point2D point;
        protected float val;
        protected List<Float> values = new ArrayList<>();
        protected List<Float> orbit = new ArrayList<>();
        protected int orbitPeriod;
        protected Status status = Status.Incomplete;

        public Pixel2D(Point2D pos) {
            point = pos;
            set((float) Math.pow(2f, point.getX()) + (float) Math.pow(2f, point.getY()));
        }

        public void set(float to) {
            val = to;

            if (status == Status.Incomplete) {
                if (val == 0) {
                    status = Status.Zero;

                    orbit.add(0f);
                    orbitPeriod = 1;
                } else if (val == 1) {
                    status = Status.One;

                    orbit.add(1f);
                    orbitPeriod = 1;
                } else if (values.contains(val)) {
                    status = Status.Cycle;

                    int startInd = values.indexOf(val);
                    orbit = Arrays.asList(Arrays.copyOfRange(values.toArray(new Float[0]), startInd, values.size()));
                    orbitPeriod = orbit.size();
                }
            }

            if (!values.contains(val)) {
                values.add(val);

                if (values.size() >= 50)
                    values.remove(0);

                if (values.size() > curMaxTrip)
                    curMaxTrip = values.size();
            }
        }
    }

    private class Runner implements Runnable { // I made the runnable a separate class to decouple the runner thread
                                               // from the main thread
        private boolean isRunning = true;

        public Runner() {
        }

        public void run() {
            long lastTime = System.nanoTime();
            float ns = 1000000000 / (float) itersPerSecond;
            long start;
            float delta = 0;

            while (isRunning) {
                start = System.nanoTime();
                delta += (start - lastTime) / ns;
                lastTime = start;

                if (delta >= 1) {
                    if (automatic)
                        tick();

                    repaint();

                    delta--;
                }
            }
        }

    }

    private class DrawPanel extends JPanel { // The class for displaying the visualization of the data
        // region Variables
        private BufferedImage img;
        // endregion

        public DrawPanel() {
            this.img = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
            setBackground(minColor);
        }

        @Override
        public void paintComponent(Graphics g) {
            Graphics2D g2d = (Graphics2D) g;
            int xInt = getWidth() / width;
            int yInt = getHeight() / height;

            // Set the image pixel colors
            if (runningThreads == 0 && shouldRebuildImage) {
                for (int y = 0; y < height; y++) {
                    for (int x = 0; x < width; x++) {
                        Pixel2D px = getPixel2DAtCoord(x, y);

                        Color col = null;

                        if (statusColors && px.status != Status.Incomplete) {
                            if (px.status == Status.Zero || px.status == Status.One) {
                                if (tripLengthColor) {
                                    col = remapColor(0, curMaxTrip, minDoneColor, maxDoneColor,
                                            (float) getTripLengthAtCoord(x, y));
                                } else {
                                    col = remapColor(curMin, curMax, minDoneColor, maxDoneColor,
                                            (float) getValueAtCoord(x, y));
                                }
                            } else if (px.status == Status.Cycle) {
                                if (tripLengthColor) {
                                    col = remapColor(0, curMaxTrip, minCycleColor, maxCycleColor,
                                            (float) getTripLengthAtCoord(x, y));
                                } else {
                                    col = remapColor(curMin, curMax, minCycleColor, maxCycleColor,
                                            (float) getValueAtCoord(x, y));
                                }
                            }
                        } else {
                            if (tripLengthColor) {
                                col = remapColor(0, curMaxTrip, minColor, maxColor,
                                        (float) getTripLengthAtCoord(x, y));
                            } else {
                                col = remapColor(curMin, curMax, minColor, maxColor,
                                        (float) getValueAtCoord(x, y));
                            }
                        }

                        img.setRGB(x, y, col.getRGB());

                        // DOESNT WORK?! colorFromValue((float) getValueAtCoord(x, y) / (float)
                        // curMax).getRGB());
                    }
                }

                shouldRebuildImage = false;
            }

            // Draw that image
            g2d.drawImage(img, 0, 0, getWidth(), getHeight(), null);

            // Draw the value for every pixel (only if it is a small image)
            if (width < 20 && height < 20) {
                g2d.setFont(font);
                FontMetrics fm = g2d.getFontMetrics();
                int h = g2d.getFontMetrics().getHeight();
                for (int y = 0; y < height; y++) {
                    for (int x = 0; x < width; x++) {
                        String str = "" + (tripLengthColor ? getTripLengthAtCoord(x, y) : getValueAtCoord(x, y));
                        int xPos = x * xInt + (xInt / 2);
                        int yPos = y * yInt + (yInt / 2);
                        g2d.setColor(labelBackgroundColor);
                        g2d.fillRect(xPos - 10, yPos - h, fm.stringWidth(str) + 20, h + 10);

                        g2d.setColor(labelTextColor);
                        g2d.drawString(str, xPos, yPos);
                    }
                }
            }
            // }

            // region Text Drawing
            g2d.setFont(font);
            FontMetrics fm = g2d.getFontMetrics();
            int ht = fm.getHeight();
            String str = "";

            // Draw pixel info
            if (pixelPos != null) {
                Pixel2D px = getPixel2DAtCoord((int) pixelPos.getX(), (int) pixelPos.getY());
                str = String.format(
                        "Pixel2D Info; Pos: (%d, %d) | Value: %f | Status: %s | Orbit: %s | Orbit Period: %d | Values Count: %d | Values: %s",
                        (int) pixelPos.getX(),
                        (int) pixelPos.getY(),
                        px.val, px.status, px.orbit.toString(), px.orbitPeriod, px.values.size(), px.values.toString());

                g2d.setColor(labelBackgroundColor);
                g2d.fillRect(45, (70 + (ht * 2)) - ht, fm.stringWidth(str) + 10, ht + 5);

                g2d.setColor(labelTextColor);
                g2d.drawString(str, 50, 70 + (ht * 2));

                // Draw selection box
                g2d.setColor(labelTextColor);
                int xPos = (int) ((int) pixelPos.getX() * xInt);
                int yPos = (int) ((int) pixelPos.getY() * yInt);
                g2d.drawRect(xPos, yPos, xInt, yInt);
            }

            // Draw current status
            str = String.format("Process Status: %s  | Max Threads: %d | Running Threads: %d | Finished: %s",
                    automatic
                            ? (finishedProcessing ? "Finished Iterating"
                                    : (doneIterating ? "Reached Max Iterations"
                                            : (paused ? "Auto Paused" : "Auto Running")))
                            : "Manual",
                    THREAD_COUNT, runningThreads, finishedProcessing);

            g2d.setColor(labelBackgroundColor);
            g2d.fillRect(45, 50 - ht, fm.stringWidth(str) + 10, ht + 5);

            g2d.setColor(labelTextColor);
            g2d.drawString(str, 50, 50);

            // Draw current info
            str = String.format(
                    "Function: %s | Iteration: %d | Average Time: %.3fms | Average Thread Time: %.3fms | Max: %f  Min: %f",
                    selectedFuncName,
                    iteration, averageTime, averageThreadTime, curMax, curMin);

            g2d.setColor(labelBackgroundColor);
            g2d.fillRect(45, (60 + ht) - ht, fm.stringWidth(str) + 10, ht + 5);

            g2d.setColor(labelTextColor);
            g2d.drawString(str, 50, 60 + ht);

            // Draw special info
            str = String.format("Fixed Point: %s | Shortest Orbit: %s (Period: %d) | Longest Orbit: %s (Period: %d)",
                    "NULL", "NULL", 0, "NULL", 0);

            g2d.setColor(labelBackgroundColor);
            g2d.fillRect(45, (80 + (ht * 3)) - ht, fm.stringWidth(str) + 10, ht + 5);

            g2d.setColor(labelTextColor);
            g2d.drawString(str, 50, 80 + (ht * 3));

            // Draw controls info
            str = "Click once to pause/unpause, float click to switch from manual to automatic iteration.";
            String str2 = "Right click once to toggle coloring based on pixel status, float right cick to toggle coloring based on value or on trip length.";

            g2d.setColor(labelBackgroundColor);
            g2d.fillRect(45, (90 + (ht * 4)) - ht, fm.stringWidth(str) + 10, ht + 5);
            g2d.fillRect(45, (100 + (ht * 5)) - ht, fm.stringWidth(str2) + 10, ht + 5);

            g2d.setColor(labelTextColor);
            g2d.drawString(str, 50, 90 + (ht * 4));
            g2d.drawString(str2, 50, 100 + (ht * 5));
            // endregion

            g2d.dispose();
        }
    }

    private class RunThread extends Thread { // The thread class for working on pixels
        private Thread t;
        private int start;
        private int end;

        public RunThread(int startInd, int endInd) {
            this.start = startInd;
            this.end = endInd;
        }

        public void run() {
            synchronized (pixels) {
                runningThreads++;

                long st = System.nanoTime();

                for (int i = start; i < end; i++) {
                    if (pixels[i].status == Status.Incomplete || pixels[i].status == Status.Cycle) {
                        float val = selectedFunction.apply(pixels[i].val);
                        pixels[i].set(val);

                        if (pixels[i].status == Status.Incomplete) {
                            finishedProcessing = false;
                        }

                        if (val > curMax)
                            curMax = val;
                        if (val < curMin)
                            curMin = val;
                    }
                }

                runningThreads--;

                currentThreadTime += (System.nanoTime() - st) / 1000000f;
            }
        }

        public void start() {
            if (t == null) {
                t = new Thread(this, "Pixel2DWorker-" + start + "-to-" + end);
                t.start();
            }
        }
    }
    // endregion

    // region Input
    @Override
    public void mouseClicked(MouseEvent e) {
        if (SwingUtilities.isRightMouseButton(e)) {
            if (e.getClickCount() == 2) {
                tripLengthColor = !tripLengthColor;
            } else {
                statusColors = !statusColors;
            }
        } else if (!finishedProcessing) {
            if (e.getClickCount() == 2) {
                automatic = !automatic;
                if (!automatic)
                    paused = false;
            } else {
                if (!automatic)
                    tick();
                else
                    paused = !paused;
            }
        }
    }

    @Override
    public void mouseEntered(MouseEvent e) {
    }

    @Override
    public void mouseExited(MouseEvent e) {
    }

    @Override
    public void mousePressed(MouseEvent e) {
    }

    @Override
    public void mouseReleased(MouseEvent e) {
    }

    @Override
    public void mouseDragged(MouseEvent e) {
    }

    @Override
    public void mouseMoved(MouseEvent e) {
        pixelPos = remapPos(e.getPoint());
    }
    // endregion

    // TODO: Fix mouse position remapping issue

    // region Helper Functions
    private Pixel2D getPixel2DAtCoord(int x, int y) {
        return pixels[(y * width) + x];
    }

    private int getTripLengthAtCoord(int x, int y) {
        return pixels[(y * width) + x].orbit.size();
    }

    private float getValueAtCoord(int x, int y) {
        return pixels[(y * width) + x].val;
    }

    private Point2D getCoordAtIndex(int index) {
        return new Point2D.Float((float) index / (float) width, (float) index % (float) width);
    }

    // private Color colorFromValue(float val) {
    // return Color.getHSBColor(lerp(0f, 1f, val), 1f, 1f);
    // }

    private float lerp(float a, float b, float t) {
        return (1f - t) * a + b * t;
    }

    private float inverseLerp(float a, float b, float val) {
        return (val - a) / (b - a);
    }

    private float remap(float min1, float max1, float min2, float max2, float val) {
        return lerp(min2, max2, inverseLerp(min1, max1, val));
    }

    private float remapClamped(float min1, float max1, float min2, float max2, float val) {
        return lerpClamped(min2, max2, inverseLerp(min1, max1, val));
    }

    private Point2D remapPos(Point2D input) {
        return new Point2D.Float(remap(0, getWidth(), 0, width, (float) input.getX()),
                remap(0, getHeight(), 0, height, (float) input.getY()));
    }

    private float clamp(float min, float max, float f) {
        return Math.max(min, Math.min(max, f));
    }

    private float lerpClamped(float a, float b, float f) {
        return clamp(a, b, a + f * (b - a));
    }

    // private Color lerpColor(Color a, Color b, float f) {
    // return new Color((int) lerpClamped(a.getRed(), b.getRed(), f),
    // (int) lerpClamped(a.getGreen(), b.getGreen(), f),
    // (int) lerpClamped(a.getBlue(), b.getBlue(), f));
    // }

    private Color remapColor(float min1, float max1, Color a, Color b, float val) {
        return new Color((int) remapClamped(min1, max1, a.getRed(), b.getRed(), val),
                (int) remapClamped(min1, max1, a.getGreen(), b.getGreen(), val),
                (int) remapClamped(min1, max1, a.getBlue(), b.getBlue(), val));
    }
    // endregion

    public enum Status {
        Incomplete,
        One,
        Zero,
        Cycle,
    }
}