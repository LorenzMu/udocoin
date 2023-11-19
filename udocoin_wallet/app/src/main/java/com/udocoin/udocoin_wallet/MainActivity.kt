package com.udocoin.udocoin_wallet

import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.graphics.BitmapFactory
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.PyException
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class MainActivity : AppCompatActivity() {
    private val TAG = "[MainActivity]"

    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }

        val py = Python.getInstance()
        val keyManagerModule = py.getModule("key_manager")

        var hasKeys = keyManagerModule.callAttr("has_keys").toBoolean()
        if(hasKeys){
            val privKey = keyManagerModule.callAttr("get_private_key").toString()
            val pubKey = keyManagerModule.callAttr("get_public_key").toString()
            findViewById<TextView>(R.id.text1).text = privKey
            findViewById<TextView>(R.id.text2).text = pubKey
        }else{
        }
        val intent = Intent(this, CodeScannerActivity::class.java)
        startActivity(intent)

        findViewById<Button>(R.id.create_keys_button).setOnClickListener{
            val keys = keyManagerModule.callAttr("create_keys").toList()//.split("|")
            val privKey = keys[0].toString()
            val pubKey = keys[1].toString()
            Log.d(TAG, privKey)
            Log.d(TAG, pubKey)
            hasKeys = true
        }

    }
}