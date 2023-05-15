// package Programs;

import java.util.ArrayList;

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
import java.awt.geom.*;
import java.awt.event.MouseEvent;
import java.awt.event.MouseWheelEvent;
import java.awt.BasicStroke;

// import jwinpointer.JWinPointerReader;
// import jwinpointer.JWinPointerReader.PointerEventListener;

public class Tree extends JFrame implements MouseInputListener, MouseWheelListener {
    private Runner runner;
    private DrawPanel panel;

    private final Font font = new Font("Arial", Font.PLAIN, 12);
    private final Color labelBackgroundColor = new Color(184, 184, 184, 200);
    private final Color labelTextColor = Color.black;

    private boolean auto = false;
    private double zoom = 1.0;

    private int maxDepth = 10;
    private double initialLength = 20.0;
    private double initialAngle = -90.0;
    private double angleRatio = 0.75;
    private double lengthRatio = 0.75;

    private double halfWidth;
    private double fourthHeight;
    private boolean dragging;
    private Point startPoint;
    private double xDiff, yDiff;
    private double xOffset, yOffset;

    public Tree(String[] args) {
        setVisible(true);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(850, 500);
        setResizable(true);
        setBackground(Color.white);

        setTitle("Tree Fractal!");

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
            new Tree(args);
        });
    }

    // region Inner Classes
    private class Runner implements Runnable { // I made the runnable a separate class to decouple the runner thread
                                               // from the main thread
        private boolean isRunning = true;

        public Runner() {
        }

        public void run() {
            long lastTime = System.nanoTime();
            float ns = 1000000000 / (float) 10;
            long start;
            float delta = 0;

            while (isRunning) {
                start = System.nanoTime();
                delta += (start - lastTime) / ns;
                lastTime = start;

                if (delta >= 1) {
                    if (auto) {
                        maxDepth++;
                        repaint();
                    }

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
            halfWidth = getWidth() / 2;
            fourthHeight = getHeight() - (getHeight() / 4);

            g2d.setColor(Color.black);
            drawTreeSegment(g2d, 0, 0, -90, initialLength, maxDepth);

            // region Text Drawing
            g2d.setFont(font);
            FontMetrics fm = g2d.getFontMetrics();
            int ht = fm.getHeight();
            ArrayList<String> messages = new ArrayList<>();

            // Draw controls info
            messages.add("Click once to grow the tree by one step, right click to toggle auto growing");
            messages.add(
                    "Scroll to zoom, alt + scroll to initial angle, control + scroll to change angle ratio, control + alt + scroll to change length ratio");

            // Draw debug info and stats
            messages.add(String.format(
                    "Auto %s | Iteration: %d | Angle Ratio: %.3f | Length Ratio: %.3f | Initial Angle: %.3f | Zoom: %.3f",
                    auto ? "On" : "Off", maxDepth,
                    (float) angleRatio, (float) lengthRatio, (float) initialAngle, (float) zoom));

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

    // Tree Drawing
    private void drawTreeSegment(Graphics2D g2d, double originX, double originY, double angle, double length,
            int depth) {
        if (depth > 0) {

            double x = originX + Math.cos(Math.toRadians(angle)) * length;
            double y = originY + Math.sin(Math.toRadians(angle)) * length;

            g2d.setStroke(new BasicStroke(depth, BasicStroke.CAP_BUTT, BasicStroke.JOIN_MITER));
            g2d.drawLine(localizeX(originX), localizeY(originY), localizeX(x), localizeY(y));

            drawTreeSegment(g2d, x, y, angle + (30 * angleRatio), length * lengthRatio, depth - 1);
            drawTreeSegment(g2d, x, y, angle - (30 * angleRatio), length * lengthRatio, depth - 1);
        }
    }

    // region Input
    @Override
    public void mouseClicked(MouseEvent e) {
        if (SwingUtilities.isRightMouseButton(e)) {
            auto = !auto;
        } else {
            if (e.isShiftDown())
                maxDepth--;
            else
                maxDepth++;
        }

        repaint();
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

        xDiff = e.getX() - startPoint.getX();
        yDiff = e.getY() - startPoint.getY();

        repaint();
    }

    @Override
    public void mouseMoved(MouseEvent e) {
    }

    @Override
    public void mouseWheelMoved(MouseWheelEvent e) {
        double scrollAmt = e.getPreciseWheelRotation();

        if (e.isControlDown() && e.isAltDown()) {
            double val = clamp(-10.0, 10.0, lengthRatio + (scrollAmt / 50.0));
            if (val > 0) {
                lengthRatio = (approx(0.75, val, 0.05) && Math.abs(scrollAmt) < 0.1 && !e.isShiftDown()) ? 0.75 : val;
            } else {
                lengthRatio = (approx(-0.75, val, 0.05) && Math.abs(scrollAmt) < 0.1 && !e.isShiftDown()) ? -0.75 : val;
            }
        } else if (e.isControlDown()) {
            double val = clamp(-10.0, 10.0, angleRatio + (scrollAmt / 50.0));
            if (val > 0) {
                angleRatio = (approx(0.75, val, 0.05) && Math.abs(scrollAmt) < 0.1 && !e.isShiftDown()) ? 0.75 : val;
            } else {
                angleRatio = (approx(-0.75, val, 0.05) && Math.abs(scrollAmt) < 0.1 && !e.isShiftDown()) ? -0.75 : val;
            }
        } else if (e.isAltDown()) {
            double val = clamp(-360.0, 360.0, initialAngle + scrollAmt);
            if (val > 90) {
                initialAngle = (approx(90.0, val, 3.0) && Math.abs(scrollAmt) < 0.25 && !e.isShiftDown()) ? 90.0 : val;
            } else {
                initialAngle = (approx(-90.0, val, 3.0) && Math.abs(scrollAmt) < 0.25 && !e.isShiftDown()) ? -90.0
                        : val;
            }
        } else {
            double val = clamp(0.0001, 500.0, zoom + scrollAmt);
            zoom = (approx(1.0, val, 0.5) && Math.abs(scrollAmt) < 0.1 && !e.isShiftDown()) ? 1.0 : val;
        }

        repaint();
    }
    // endregion

    // region Helper Functions
    private int localizeX(double x) {
        return (int) (x * zoom + (halfWidth + (xOffset + xDiff)));
    }

    private int localizeY(double y) {
        return (int) (y * zoom + (fourthHeight + (yOffset + yDiff)));
    }

    private double lerp(double a, double b, double t) {
        return (1.0 - t) * a + b * t;
    }

    private double inverseLerp(double a, double b, double val) {
        return (val - a) / (b - a);
    }

    private double remap(double min1, double max1, double min2, double max2, double val) {
        return lerp(min2, max2, inverseLerp(min1, max1, val));
    }

    private double remapClamped(double min1, double max1, double min2, double max2, double val) {
        return lerpClamped(min2, max2, inverseLerp(min1, max1, val));
    }

    private double clamp(double min, double max, double f) {
        return Math.max(min, Math.min(max, f));
    }

    private double lerpClamped(double a, double b, double f) {
        return clamp(a, b, a + f * (b - a));
    }

    private boolean approx(double a, double b, double threshold) {
        return Math.abs(a - b) < threshold;
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