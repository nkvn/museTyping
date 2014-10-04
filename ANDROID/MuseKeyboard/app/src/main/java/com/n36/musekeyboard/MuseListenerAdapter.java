package com.n36.musekeyboard;

/**
 * Created by jonathantom on 2014-10-04.
 */
public abstract class MuseListenerAdapter implements MuseIOReceiver.MuseDataListener {

    @Override
    public void receiveMuseElementsAlpha(MuseIOReceiver.MuseConfig config, float[] alpha) {

    }

    @Override
    public void receiveMuseElementsBeta(MuseIOReceiver.MuseConfig config, float[] beta) {

    }

    @Override
    public void receiveMuseElementsTheta(MuseIOReceiver.MuseConfig config, float[] theta) {

    }

    @Override
    public void receiveMuseElementsDelta(MuseIOReceiver.MuseConfig config, float[] delta) {

    }

    @Override
    public void receiveMuseEeg(MuseIOReceiver.MuseConfig config, float[] eeg) {

    }

    @Override
    public void receiveMuseAccel(MuseIOReceiver.MuseConfig config, float[] accel) {

    }

    @Override
    public void receiveMuseBattery(MuseIOReceiver.MuseConfig config, int[] battery) {

    }

    @Override
    public void receiveJawClench(MuseIOReceiver.MuseConfig config, int[] i) {

    }

    @Override
    public void receiveTouchingForehead(MuseIOReceiver.MuseConfig config, int[] i) {

    }

    @Override
    public void receiveBlink(MuseIOReceiver.MuseConfig config, int[] i) {

    }
}
