package com.udocoin.udocoin_wallet

import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Point
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.view.Display
import android.view.WindowManager
import android.widget.Button
import android.widget.ImageView
import android.widget.Toast
import androidmads.library.qrgenearator.QRGContents
import androidmads.library.qrgenearator.QRGEncoder
import com.udocoin.udocoin_wallet.modules.KeyManager
import java.security.Key
import java.security.PublicKey

class ProfileActivity : AppCompatActivity() {
    private lateinit var keyManager: KeyManager
    private val TAG = "[PROFILE ACTIVITY]"
    lateinit var qrEncoder: QRGEncoder
    lateinit var bitmap: Bitmap
    private lateinit var qrIV: ImageView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        qrIV = findViewById(R.id.idIVQrcode)
        keyManager = KeyManager.getInstance()
        // Create qr code
        /** go to login activity if there are no keys */
        if(!keyManager.hasValidKeys(this)){
            Log.d(TAG,"No keys found. Returning to Login Activity")
            Toast.makeText(this, "No keys found.", Toast.LENGTH_SHORT).show()
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
            finish()
        }
        val publicKey = keyManager.getPublicKey(this)
        generateQrCode(publicKey!!)
        findViewById<Button>(R.id.reset_keys).setOnClickListener { resetKeys() }
        findViewById<Button>(R.id.go_back).setOnClickListener {
            onBackPressed()
        }
    }

    private fun generateQrCode(publicKey: String){
        val windowManager: WindowManager = getSystemService(WINDOW_SERVICE) as WindowManager

        val display: Display = windowManager.defaultDisplay

        val point: Point = Point()
        display.getSize(point)

        val width = point.x
        val height = point.y

        var dimen = if (width < height) width else height
        dimen = dimen * 3 / 4

        qrEncoder = QRGEncoder(publicKey, null, QRGContents.Type.TEXT, dimen)

        try {
            bitmap = qrEncoder.getBitmap(0)

            qrIV.setImageBitmap(bitmap)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun resetKeys(){
        keyManager.setPrivateKey(this,"")
        keyManager.setPublicKey(this,"")
        val intent = Intent(this, LoginActivity::class.java)
        startActivity(intent)
    }
}