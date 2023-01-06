package Programs;

import java.util.ArrayList;
import java.util.function.Function;

import javax.swing.JFrame;
import javax.swing.SwingUtilities;
import javax.swing.event.MouseInputListener;
import java.awt.event.MouseWheelListener;
import javax.swing.JPanel;

import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Point;
import java.awt.event.MouseEvent;
import java.awt.event.MouseWheelEvent;
import java.awt.BasicStroke;
import java.awt.geom.GeneralPath;

public class Grapher extends JFrame implements MouseInputListener, MouseWheelListener {
    double R = 3.4;
    private final Function<Double, Double> function = (in) -> {
        return R * in * (1.0 - in);
    };

    private Runner runner;
    private DrawPanel panel;

    private int iteration;

    private final Font font = new Font("Arial", Font.PLAIN, 12);
    private final Color labelBackgroundColor = new Color(184, 184, 184, 200);
    private final Color labelTextColor = Color.black;

    private boolean dragging;
    private Point startPoint;
    private double xDiff, yDiff;
    private double xOffset, yOffset;
    private double scale = 1.0;
    private double scalar = (this.getWidth() / 2) / scale;

    public Grapher(String[] args) {
        setVisible(true);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(500, 500);
        setResizable(true);
        setBackground(Color.white);

        // Add the input listeners
        addMouseListener(this);
        addMouseMotionListener(this);
        addMouseWheelListener(this);

        // Create the automatic runner
        runner = new Runner();
        new Thread(runner).start();

        // Create the draw panel
        panel = new DrawPanel();
        add(panel);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new Grapher(args);
        });
    }

    // The primary function. Iterates over every pixel and applies the selected
    // function to its value.
    private void tick() {
        new Thread(new Runnable() {
            public void run() {
                iteration++;

            }
        }).start();
    }

    // region Inner Classes
    private class Runner implements Runnable { // I made the runnable a separate class to decouple the runner thread
                                               // from the main thread
        private boolean isRunning = true;

        public Runner() {
        }

        public void run() {
            long lastTime = System.nanoTime();
            float ns = 1000000000 / (float) 60;
            long start;
            float delta = 0;

            while (isRunning) {
                start = System.nanoTime();
                delta += (start - lastTime) / ns;
                lastTime = start;

                if (delta >= 1) {
                    repaint();

                    delta--;
                }
            }
        }

    }

    private class DrawPanel extends JPanel { // The class for displaying the visualization of the data
        public DrawPanel() {
            setBackground(Color.white);
        }

        @Override
        public void paintComponent(Graphics g) {
            Graphics2D g2d = (Graphics2D) g;

            // region Draw Function
            // w is x, and h is y (as in x/y values in a graph)
            int w = this.getWidth() / 2;
            int h = this.getHeight() / 2;
            scalar = 1.0 / ((double) w / scale);

            // Draw axes
            g2d.setStroke(new BasicStroke(2));
            g2d.setColor(Color.black);
            g2d.drawLine(0, h + (int) (yOffset + yDiff), w * 2, h + (int) (yOffset + yDiff));
            g2d.drawLine(w + (int) (xOffset + xDiff), 0, w + (int) (xOffset + xDiff), h * 2);
            // drawGrid(g2d, w, h, 30);

            // Draw labels
            g2d.drawString("0", (w + (int) (xOffset + xDiff)) - 7, (h + (int) (yOffset + yDiff)) + 13);

            // Draw function(s)
            g2d.setStroke(new BasicStroke(2));
            g2d.setColor(Color.red);

            GeneralPath p = new GeneralPath();

            p.moveTo(0, h - 0);
            for (int x = -w; x <= w; x++) {
                p.lineTo(w + x,
                        h - (int) Math.round(localizeYValue(Math.cos(((double) x - (xOffset + xDiff)) * scalar))));
            }
            g2d.draw(p);
            // endregion

            // region Text Drawing
            g2d.setFont(font);
            FontMetrics fm = g2d.getFontMetrics();
            int ht = fm.getHeight();
            ArrayList<String> messages = new ArrayList<>();

            // Draw controls info
            messages.add("Click once to pause/unpause, double click to switch from manual to automatic iteration.");
            messages.add(
                    "Right click once to toggle coloring based on pixel status, double right cick to toggle coloring based on value or on trip length.");

            // Draw debug info and stats
            messages.add(String.format("Scale: %.3f", (float) scale));

            for (int i = 0; i < messages.size(); i++) {
                g2d.setColor(labelBackgroundColor);
                g2d.fillRect(45, 15 + ((10 * (i + 1)) + (ht * i)) - ht, fm.stringWidth(messages.get(i)) + 10, ht + 5);

                g2d.setColor(labelTextColor);
                g2d.drawString(messages.get(i), 50, 15 + (10 * (i + 1)) + (ht * i));
            }
            // endregion

            g2d.dispose();
        }
    }
    // endregion

    // region Drawing
    public void drawGrid(Graphics2D g2d, double w, double h, int gridSize) {
        g2d.setColor(Color.gray);

        // Draws the horizontal and vertical grid lines every [gridSize] units
        AxisTickCalculator vert = new AxisTickCalculator(AxisTickCalculator.Direction.X, getWidth() * (1.0 / scalar),
                0 - (xOffset + xDiff),
                getWidth() - (xOffset + xDiff), font, 1);

        // Vertical lines
        ArrayList<Double> ticks = new ArrayList<Double>(vert.getTickLocations());

        for (int i = 0; i < ticks.size(); i++) {
            double val = ticks.get(i);
            double localVal = localizeXValue(val);

            if (localVal % 10 == 0)
                g2d.setStroke(new BasicStroke(3));

            g2d.drawLine((int) (w + val), 0, (int) (w + val), (int) getHeight()); // Vertical
            g2d.setStroke(new BasicStroke(1));

            g2d.drawString(String.format("%.3f", (float) localVal), (int) (w + val) + 7, (int) h + 13);
        }

        // Horizontal Lines
        /*
         * ticks = new ArrayList<Double>(horiz.getTickLocations());
         * 
         * for (int i = 0; i < ticks.size(); i++) {
         * double val = ticks.get(i);
         * 
         * if (val % 10 == 0)
         * g2d.setStroke(new BasicStroke(3));
         * 
         * g2d.drawLine(0, (int) val, (int) w, (int) val); // Horizontal
         * g2d.setStroke(new BasicStroke(1));
         * 
         * g2d.drawString(String.format("%.3f", (float) val), (int) w + 7, (int) val +
         * 13);
         * }
         */
    }
    // endregion

    // region Input
    @Override
    public void mouseClicked(MouseEvent e) {
        if (SwingUtilities.isRightMouseButton(e)) {
            repaint();
        } else {

            tick();
            repaint();
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
        startPoint = e.getPoint();
    }

    @Override
    public void mouseReleased(MouseEvent e) {
        if (dragging) {
            dragging = false;
            xOffset += xDiff;
            yOffset += yDiff;

            xDiff = 0;
            yDiff = 0;
        }
    }

    @Override
    public void mouseDragged(MouseEvent e) {
        dragging = true;
        Point pt = e.getPoint();
        xDiff = pt.getX() - startPoint.getX();
        yDiff = pt.getY() - startPoint.getY();

        repaint();
    }

    @Override
    public void mouseMoved(MouseEvent e) {
    }

    @Override
    public void mouseWheelMoved(MouseWheelEvent e) {
        if (e.getUnitsToScroll() < 0) {
            scale = Math.min(500.0, scale / 1.05);
        } else if (e.getUnitsToScroll() > 0) {
            scale = Math.max(0.02, scale * 1.05);
        }

        repaint();
    }
    // endregion

    // region Helper Functions
    private double localizeXValue(double x) {
        return (x - (xOffset + xDiff)) * (1.0 / scalar);
    }

    private double localizeYValue(double y) {
        return (y - (yOffset + yDiff)) * (1.0 / scalar);
    }

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
}