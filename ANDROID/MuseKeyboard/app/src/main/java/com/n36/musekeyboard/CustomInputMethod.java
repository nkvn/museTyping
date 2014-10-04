package com.n36.musekeyboard;

import android.content.Intent;
import android.inputmethodservice.InputMethodService;
import android.os.Looper;
import android.support.v4.view.ViewPager;
import android.util.Log;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputConnection;
import android.widget.TextView;

import java.io.IOException;
import java.util.Timer;
import java.util.TimerTask;

/**
 * Created by jonathantom on 2014-10-03.
 */
public class CustomInputMethod extends InputMethodService {

    private static final int PORT = 5000;
    private static final boolean UDP = false;
    private static final int TIMER_DELAY = 1000;

    private MuseIOReceiver mReceiver;

    private MuseIOReceiver.MuseDataListener mDataListener = new MuseListenerAdapter() {

        @Override
        public void receiveMuseAccel(MuseIOReceiver.MuseConfig config, float[] accel) {
            Log.d("MUSE_TAG", String.format("Accel: %s %s %s", accel[0], accel[1], accel[2]));
        }

        @Override
        public void receiveBlink(MuseIOReceiver.MuseConfig config, int[] i) {
            onInput(intToString(mCurrentChar));
        }
    };

    private TextView mTextView;
    private int mCurrentChar = 0;
    private Timer mTimer;

    @Override
    public void onCreate() {
        super.onCreate();

        mReceiver = new MuseIOReceiver(PORT, UDP);
        mReceiver.registerMuseDataListener(mDataListener);
    }

    @Override
    public void onWindowShown() {
        super.onWindowShown();
        try {
            mReceiver.connect();
            mCurrentChar = 0;
            updateTextView(intToString(mCurrentChar));
            mTimer = new Timer(true);
            mTimer.schedule(new TimerTask() {
                @Override
                public void run() {
                    mCurrentChar = (mCurrentChar+1) % 26;
                    if (mTextView != null) {
                        mTextView.post(new Runnable() {
                            @Override
                            public void run() {
                                updateTextView(intToString(mCurrentChar));
                            }
                        });
                    }
                }
            }, TIMER_DELAY, TIMER_DELAY);
            Log.d("MUSE_TAG", "CONNECTED");
        } catch (IOException e) {
            e.printStackTrace();
            Log.d("MUSE_TAG", "FAILED: " + e.getMessage());
            updateTextView("Failed to\nConnect");
        }
    }

    private String intToString(int i) {
        return String.valueOf((char) (i + 'A'));
    }

    private void updateTextView(final String s) {
        if (mTextView == null) {
            return;
        }
        if (Looper.myLooper() == Looper.getMainLooper()) {
            mTextView.setText(s);
        } else {
            mTextView.post(new Runnable() {
                @Override
                public void run() {
                    if (mTextView != null) {
                        mTextView.setText(s);
                    }
                }
            });
        }
    }

    @Override
    public void onWindowHidden() {
        super.onWindowHidden();
        mReceiver.disconnect();
        mReceiver.unregisterMuseDataListener(mDataListener);
        if (mTimer != null) {
            mTimer.cancel();
            mTimer.purge();
        }
        Log.d("MUSE_TAG", "DISCONNECTED");
    }

    public void onInput(String input) {
        final InputConnection connection = getCurrentInputConnection();
        connection.commitText(input, 1);
    }

    @Override
    public View onCreateInputView() {
        final View view = getLayoutInflater().inflate(R.layout.input_view, null);

        mTextView = (TextView) view.findViewById(R.id.text);

        view.findViewById(R.id.button).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                onInput(intToString(mCurrentChar));
            }
        });

        return view;
    }
}
