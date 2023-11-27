package com.udocoin.udocoin_wallet

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.udocoin.udocoin_wallet.modules.BlockchainManager
import com.udocoin.udocoin_wallet.modules.KeyManager

class MainActivity : AppCompatActivity() {
    private val TAG = "[MAIN ACTIVITY]"
    lateinit var keyManager: KeyManager
    lateinit var blockchainManager: BlockchainManager

    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        Log.d(TAG,"HELLO FROM MAIN ACTIVITY ON CREATE")
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        keyManager = KeyManager.getInstance()
        blockchainManager = BlockchainManager.getInstance()

        /** go to login activity if there are no keys */
        if(!keyManager.hasValidKeys(this)){
            Log.d(TAG,"No keys found. Returning to Login Activity")
            Toast.makeText(this, "No keys found.",Toast.LENGTH_SHORT).show()
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
            finish()
        }
        findViewById<Button>(R.id.create_transaction).setOnClickListener { startTransaction() }
        findViewById<Button>(R.id.view_profile).setOnClickListener {
            val intent = Intent(this,ProfileActivity::class.java)
            startActivity(intent)
        }
        val balance = blockchainManager.getBalance(this)
        findViewById<TextView>(R.id.balance_text).text = "Balance: $balance"
        if(balance == "N/a"){
            Toast.makeText(this,"Couldn't connect to any Server.",Toast.LENGTH_LONG).show()
        }
    }


    private fun startTransaction(){
        val intent = Intent(this, CodeScannerActivity::class.java)
        intent.putExtra("redirectActivity","TransactionActivity")
        startActivity(intent)
    }
}