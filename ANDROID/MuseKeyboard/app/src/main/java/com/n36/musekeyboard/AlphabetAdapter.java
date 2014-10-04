package com.n36.musekeyboard;

import android.animation.ArgbEvaluator;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

/**
 * Created by jonathantom on 2014-10-04.
 */
public class AlphabetAdapter extends FragmentPagerAdapter {

    private final static String LETTER_ARG = "asdasd";

    public AlphabetAdapter(FragmentManager fm) {
        super(fm);
    }

    @Override
    public Fragment getItem(int position) {
        return LetterFragment.newInstance((char) (position + 'A'));
    }

    @Override
    public int getCount() {
        return 26;
    }

    public static class LetterFragment extends Fragment {

        public static LetterFragment newInstance(char c) {
            final LetterFragment fragment = new LetterFragment();

            final Bundle args = new Bundle();
            args.putChar(LETTER_ARG, c);
            fragment.setArguments(args);

            return fragment;
        }

        @Override
        public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
            final TextView textView = new TextView(container.getContext());

            textView.setText(getArguments().getChar(LETTER_ARG));

            return textView;
        }
    }

}
