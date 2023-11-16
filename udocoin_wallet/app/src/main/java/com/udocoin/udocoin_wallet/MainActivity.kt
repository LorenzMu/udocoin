package com.udocoin.udocoin_wallet

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.BitmapFactory
import android.os.Bundle
import android.util.Log
import android.view.inputmethod.InputMethodManager
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.PyException
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.google.android.material.tabs.TabLayout.TabGravity
import kotlin.reflect.typeOf

class MainActivity : AppCompatActivity() {
    val TAG = "[MainActivity]"

    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }

        val py = Python.getInstance()
        val keyManagerModule = py.getModule("key_manager")

        var pubKeyFileName = "pub_key.pub"
        var privKeyFileName = "priv_key"

        val keyDirectory = keyManagerModule.callAttr("get_directory")

        val pubKeyExists = keyManagerModule.callAttr(
            "key_exists",
            keyDirectory,
            pubKeyFileName
        ).toBoolean()
        val privKeyExists = keyManagerModule.callAttr(
            "key_exists",
            keyDirectory,
            privKeyFileName
        ).toBoolean()
        findViewById<TextView>(R.id.text1).text = "Pubkeypath = $keyDirectory/$pubKeyFileName"
        findViewById<TextView>(R.id.text2).text = "Privkeypath = $keyDirectory/$privKeyFileName"

        findViewById<Button>(R.id.create_keys_button).setOnClickListener{
            val keys = keyManagerModule.callAttr("create_keys",keyDirectory).toString().split("|")
            val privKey = keys[0]
            val pubKey = keys[1]
            Log.d(TAG,privKey)
            Log.d(TAG,pubKey)
        }
//        val hasKeys = moduleKeyManager.callAttr()
//
//        findViewById<Button>(R.id.button).setOnClickListener {
//            try {
//                val bytes = module.callAttr(
//                    "plot",
//                    findViewById<EditText>(R.id.etX).text.toString(),
//                    findViewById<EditText>(R.id.etY).text.toString()
//                )
//                    .toJava(ByteArray::class.java)
//
//                val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
//                findViewById<ImageView>(R.id.imageView).setImageBitmap(bitmap)
//
//                currentFocus?.let {                    (getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager)
//                        .hideSoftInputFromWindow(it.windowToken,0)
//                }
//            } catch (e: PyException) {
//                Toast.makeText(this, e.message, Toast.LENGTH_LONG).show()
//            }
//        }

    }
}