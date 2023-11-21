package com.udocoin.udocoin_wallet

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.udocoin.udocoin_wallet.modules.KeyManager
import com.udocoin.udocoin_wallet.modules.TransactionManager
import java.lang.Float

class TransactionActivity : AppCompatActivity() {
    private val TAG = "[TRANSACTION ACTIVITY]"
    lateinit var keyManager: KeyManager
    lateinit var transactionManager: TransactionManager
    lateinit var privateKey: String
    lateinit var publicKey: String
    lateinit var destinationPublicKey: String
    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_transaction)
        keyManager = KeyManager.getInstance()
        transactionManager = TransactionManager.getInstance()
        try{
            destinationPublicKey = intent.getStringExtra("scanResult")!!
            privateKey = keyManager.getPrivateKey(this)!!
            publicKey = keyManager.getPublicKey(this)!!
        }catch (e: java.lang.Exception){
            Toast.makeText(this,"Error finding keys.",Toast.LENGTH_SHORT).show()
            val intent = Intent(this,MainActivity::class.java)
            startActivity(intent)
            finish()
        }
        findViewById<TextView>(R.id.destination_public_key).text = destinationPublicKey
        findViewById<TextView>(R.id.private_key).text = privateKey
        findViewById<TextView>(R.id.public_key).text = publicKey
        findViewById<Button>(R.id.send_button).setOnClickListener { sendTransaction() }
    }

    private fun sendTransaction(){
        val amount: kotlin.Float
        try{
            amount = Float.valueOf(findViewById<EditText>(R.id.transaction_amount).text.toString())
        }catch (e: java.lang.Exception){
            Toast.makeText(this,"Invalid amount format.",Toast.LENGTH_SHORT).show()
            return
        }
        val transaction = transactionManager.createTransaction(
            this,
            privateKey,
            publicKey,
            destinationPublicKey,
            amount
        )
        Toast.makeText(this,transaction.toString(),Toast.LENGTH_SHORT).show()
        Log.d(TAG,transaction.toString())
    }
}