package com.n36.musekeyboard;

import android.inputmethodservice.InputMethodService;
import android.os.AsyncTask;
import android.os.Looper;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.View;
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
    private static final boolean UDP = true;

    private MuseIOReceiver mReceiver;

    private MuseIOReceiver.MuseDataListener mDataListener = new MuseListenerAdapter() {

        int mPrevBlink;

        @Override
        public void receiveBlink(MuseIOReceiver.MuseConfig config, int[] i) {
            final int blink = i[0];
            if (blink == 1 && mPrevBlink != 1) {
                onInput(intToString((mCurrentChar + 25) % 26));
            }
            mPrevBlink = blink;
        }

    };

    private TextView mTextView;
    private int mCurrentChar = 0;
    private Timer mTimer;

    @Override
    public void onCreate() {
        super.onCreate();
    }

    @Override
    public void onWindowShown() {
        super.onWindowShown();
        mCurrentChar = 0;
        updateTextView(intToString(mCurrentChar));
        final int timerDelay = Integer.valueOf(PreferenceManager.getDefaultSharedPreferences(getApplicationContext()).getString("cycle_delay", "1000"));
        mReceiver = new MuseIOReceiver(PORT, UDP);
        mReceiver.registerMuseDataListener(mDataListener);
        try {
            mReceiver.connect();
            mTimer = new Timer(true);
            mTimer.schedule(new TimerTask() {
                @Override
                public void run() {
                    mCurrentChar = (mCurrentChar + 1) % 26;
                    if (mTextView != null) {
                        mTextView.post(new Runnable() {
                            @Override
                            public void run() {
                                updateTextView(intToString(mCurrentChar));
                            }
                        });
                    }
                }
            }, timerDelay, timerDelay);
            Log.d("MUSE_TAG", "asd");
        } catch (IOException e) {
            updateTextView("Error");
            Log.d("MUSE_TAG", "asd2");
            e.printStackTrace();
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
    }

    public void onInput(String input) {
        final InputConnection connection = getCurrentInputConnection();
        connection.commitText(input, 1);
    }

    @Override
    public View onCreateInputView() {
        final View view = getLayoutInflater().inflate(R.layout.input_view, null);

        mTextView = (TextView) view.findViewById(R.id.text);

        return view;
    }

}
