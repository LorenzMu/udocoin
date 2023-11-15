package com.udocoin.udocoin_wallet

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import com.chaquo.python.Python
import kotlinx.android.synthetic.main.activity_main.*

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        hello_textview.text = getPythonHelloWorld()
    }

    private fun getPythonHelloWorld(): String {
        val python = Python.getInstance()
        val pythonFile = python.getModule("helloworldscript")
        return pythonFile.callAttr("helloworld").toString()
    }
}






