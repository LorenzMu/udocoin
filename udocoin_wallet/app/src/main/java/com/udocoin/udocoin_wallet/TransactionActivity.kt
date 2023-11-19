package com.udocoin.udocoin_wallet

import android.annotation.SuppressLint
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class TransactionActivity : AppCompatActivity() {
    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_transaction)
        findViewById<TextView>(R.id.text1).text = "Target key: \n" + intent.getStringExtra("scan_result")
        findViewById<TextView>(R.id.text2).text = "Target key: \n" + intent.getStringExtra("scan_result")
        findViewById<TextView>(R.id.text3).text = "Target key: \n" + intent.getStringExtra("scan_result")
    }

}