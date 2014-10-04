package com.n36.musekeyboard;

import java.io.IOException;
import java.util.HashMap;
import java.util.concurrent.CopyOnWriteArrayList;

import com.google.gson.FieldNamingPolicy;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.sojamo.ix.netP5.TcpClient;
import com.sojamo.ix.oscP5.OscMessage;
import com.sojamo.ix.oscP5.OscP5;

/**
 * The responsibility of this class is to receive Muse data from Muse-IO via the
 * OSC protocol. It will then pass any brainwave information that is received to
 * any registered MuseDataListeners.
 * <p>
 * There is a single muse per connection policy. So, UDP ports should only
 * receive data from a single muse. TCP ports can have multiple connections and
 * so can support multiple muses on a single port for each connection.
 * <p>
 * Makes use of a modified version of the oscp5 library. Modifications to the
 * library include some bug fixes with regards to disconnecting from a TCP
 * socket and better exception handling.
 */
public class MuseIOReceiver {

    /**
     * A data structure containing all of the various values obtained from a
     * /muse/config OSC message from muse-io
     */
    public static class MuseConfig {
        public String macAddr, serialNumber, preset, eegChannelLayout,
                eegUnits, accUnits;
        public boolean filtersEnabled, batteryDataEnabled, compressionEnabled,
                accDataEnabled, drlrefDataEnabled, errorDataEnabled;
        int notchFrequencyHz, eegSampleFrequencyHz, eegOutputFrequencyHz,
                eegChannelCount, eegSameplesBitwidth, eegDownsample, afeGain,
                batteryPercentRemaining, batteryMillivolts,
                accSampleFrequencyHz, dsprefSampleFrequencyHz;
        double eegConversionFactor, drlrefConversionFactor,
                accConversionFactor;

        private MuseConfig() {
        }
    }

    /**
     * A listener interface for incoming data. Implement this interface and
     * register the listener with
     * {@link MuseIOReceiver#registerMuseDataListener(MuseDataListener)} to
     * receive data. Data is received on a separate connection thread.
     */
    public interface MuseDataListener {
        void receiveMuseElementsAlpha(MuseConfig config, float[] alpha);

        void receiveMuseElementsBeta(MuseConfig config, float[] beta);

        void receiveMuseElementsTheta(MuseConfig config, float[] theta);

        void receiveMuseElementsDelta(MuseConfig config, float[] delta);

        void receiveMuseEeg(MuseConfig config, float[] eeg);

        void receiveMuseAccel(MuseConfig config, float[] accel);

        void receiveMuseBattery(MuseConfig config, int[] battery);

        void receiveJawClench(MuseConfig config, int[] i);

        void receiveTouchingForehead(MuseConfig config, int[] i);

        void receiveBlink(MuseConfig config, int[] i);
    }

    private final int PORT;

    private final boolean UDP;

    private final CopyOnWriteArrayList<MuseDataListener> listeners;

    private OscReceiver osc;

    /**
     * Creates an instance that can listen for muse-io OSC messages using the
     * default muse-io port (5000) using the default communication protocol
     * (TCP).
     */
    public MuseIOReceiver() {
        this(5000, false);
    }

    /**
     * Creates an instance that can listen for muse-io OSC messages using the
     * specified port using the default communication protocol (TCP).
     *
     * @param port
     *            Specified port.
     */
    public MuseIOReceiver(int port) {
        this(port, false);
    }

    /**
     * Creates an instance that can listen for muse-io OSC messages using the
     * specified port using the specified communication protocol.
     *
     * @param port
     *            Specified port.
     * @param udp
     *            Specified communication protocol. True if using UDP, otherwise
     *            using TCP.
     */
    public MuseIOReceiver(int port, boolean udp) {
        this.PORT = port;
        this.UDP = udp;
        this.listeners = new CopyOnWriteArrayList<MuseDataListener>();
    }

    /**
     * Registers the specified listener to receive muse data if it has not
     * already been registered to do so, otherwise does nothing.
     *
     * @param listener
     *            Specified listener.
     */
    public void registerMuseDataListener(MuseDataListener listener) {
        this.listeners.addIfAbsent(listener);
    }

    /**
     * Unregisters the specified listener if it is currently registered,
     * otherwise does nothing.
     *
     * @param listener
     *            Specified listener.
     */
    public void unregisterMuseDataListener(MuseDataListener listener) {
        this.listeners.remove(listener);
    }

    /**
     * Binds to the port that was selected for use during construction.
     *
     * @throws IOException
     *             if the socket is already bound.
     */
    public void connect() throws IOException {
        this.osc = new OscReceiver(this.PORT, this.UDP);
    }

    /**
     * Unbinds the socket to stop listening for OSC messages if it is currently
     * bound, otherwise does nothing.
     */
    public void disconnect() {
        if (this.osc != null) {
            this.osc.disconnect();
            this.osc = null;
        }
    }

    private class OscReceiver {

        private final HashMap<TcpClient, MuseConfig> museConfigs;

        private OscP5 osc;

        public OscReceiver(int port, boolean udp) throws IOException {
            this.museConfigs = new HashMap<TcpClient, MuseConfig>();
            if (udp)
                this.osc = new OscP5(this, port);
            else
                this.osc = new OscP5(this, port, OscP5.TCP);
        }

        public synchronized void disconnect() {
            this.osc.dispose();
            this.osc = null;
        }

        // The oscp5 library is kind of weird in that it makes use of reflection
        // to send OSC messages to this method. The reason for this is that the
        // library is intended for use for people working with Processing. I use
        // this library because it supports a good variety of data types, but
        // you could make use of a different library if you want.
        @SuppressWarnings("unused")
        public synchronized void oscEvent(final OscMessage msg) {
            MuseConfig config = null;

            // Reuse the configuration instead of creating a new one each time
            // a muse configuration message is received.
            if (MuseIOReceiver.this.UDP) {
                config = this.museConfigs.get(null);
            } else {
                config = this.museConfigs.get(msg.tcpConnection());
            }

            String addressPattern = msg.addrPattern();
            if (config == null && addressPattern.equals("/muse/config")) {
                Gson gson = new GsonBuilder().setFieldNamingPolicy(
                        FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES).create();

                // Parse the JSON muse configuration message.
                MuseConfig newConfig = gson.fromJson(msg.get(0).stringValue(),
                        MuseConfig.class);

                if (MuseIOReceiver.this.UDP) {
                    this.museConfigs.put(null, newConfig);
                } else {
                    this.museConfigs.put(msg.tcpConnection(), newConfig);
                }
            }

            // Once a muse configuration message has been received then I can
            // figure out from which muse messages are coming from and then
            // start to send the information received to the listeners.
            else if (config != null) {
                if (addressPattern.equals("/muse/dsp/elements/alpha"))
                    this.sendAlpha(config, msg);
                else if (addressPattern.equals("/muse/dsp/elements/beta"))
                    this.sendBeta(config, msg);
                else if (addressPattern.equals("/muse/dsp/elements/theta"))
                    this.sendTheta(config, msg);
                else if (addressPattern.equals("/muse/dsp/elements/delta"))
                    this.sendDelta(config, msg);
                else if (addressPattern.equals("/muse/eeg"))
                    this.sendEeg(config, msg);
                else if (addressPattern.equals("/muse/acc"))
                    this.sendAccel(config, msg);
                else if (addressPattern.equals("/muse/batt"))
                    this.sendBattery(config, msg);
                else if (addressPattern.equals("/muse/dsp/elements/jaw_clench"))
                    this.sendJawClench(config, msg);
                else if (addressPattern.equals("/muse/dsp/elements/touching_forehead"))
                    this.sendTouchingForehead(config, msg);
                else if (addressPattern.equals("/muse/dsp/blink"))
                    this.sendBlink(config, msg);
            }
        }

        private float[] getFloatVals(OscMessage msg) {
            int numChannels = msg.typetag().length();
            float[] floatVals = new float[numChannels];
            for (int i = 0; i < numChannels; i++)
                floatVals[i] = msg.get(i).floatValue();
            return floatVals;
        }

        private int[] getIntVals(OscMessage msg) {
            int numChannels = msg.typetag().length();
            int[] intVals = new int[numChannels];
            for (int i = 0; i < numChannels; i++)
                intVals[i] = msg.get(i).intValue();
            return intVals;
        }

        private void sendAlpha(MuseConfig config, OscMessage msg) {
            float[] alpha = this.getFloatVals(msg);
            for (MuseDataListener l : MuseIOReceiver.this.listeners) {
                l.receiveMuseElementsAlpha(config, alpha);
            }
        }

        private void sendBeta(MuseConfig config, OscMessage msg) {
            float[] beta = this.getFloatVals(msg);
            for (MuseDataListener l : MuseIOReceiver.this.listeners) {
                l.receiveMuseElementsBeta(config, beta);
            }
        }

        private void sendTheta(MuseConfig config, OscMessage msg) {
            float[] theta = this.getFloatVals(msg);
            for (MuseDataListener l : MuseIOReceiver.this.listeners) {
                l.receiveMuseElementsTheta(config, theta);
            }
        }

        private void sendDelta(MuseConfig config, OscMessage msg) {
            float[] delta = this.getFloatVals(msg);
            for (MuseDataListener l : MuseIOReceiver.this.listeners) {
                l.receiveMuseElementsDelta(config, delta);
            }
        }

        private void sendEeg(MuseConfig config, OscMessage msg) {
            float[] eeg = this.getFloatVals(msg);
            for (MuseDataListener l : MuseIOReceiver.this.listeners) {
                l.receiveMuseEeg(config, eeg);
            }
        }

        private void sendAccel(MuseConfig config, OscMessage msg) {
            float[] accel = this.getFloatVals(msg);
            for (MuseDataListener l : MuseIOReceiver.this.listeners) {
                l.receiveMuseAccel(config, accel);
            }
        }

        private void sendBattery(MuseConfig config, OscMessage msg) {
            int[] battery = this.getIntVals(msg);
            for (MuseDataListener l : MuseIOReceiver.this.listeners) {
                l.receiveMuseBattery(config, battery);
            }
        }

        private void sendJawClench(MuseConfig config, OscMessage msg) {
            int[] jaw = this.getIntVals(msg);
            for (MuseDataListener l : MuseIOReceiver.this.listeners) {
                l.receiveJawClench(config, jaw);
            }
        }

        private void sendTouchingForehead(MuseConfig config, OscMessage msg) {
            int[] forehead = this.getIntVals(msg);
            for (MuseDataListener l : MuseIOReceiver.this.listeners) {
                l.receiveTouchingForehead(config, forehead);
            }
        }

        private void sendBlink(MuseConfig config, OscMessage msg) {
            int[] blink = this.getIntVals(msg);
            for (MuseDataListener l : MuseIOReceiver.this.listeners) {
                l.receiveBlink(config, blink);
            }
        }
    }
}
