package com.udocoin.udocoin_wallet.modules

import android.content.Context
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class BlockchainManager {
    companion object {
        private var instance: BlockchainManager? = null
        fun getInstance(): BlockchainManager = instance ?: synchronized(this){
            instance ?: BlockchainManager().also { instance = it }
        }
    }

    private val transactionsModule = "transactions" // transactions.py
    private val blockchainConnectionModule = "bc_connection" // bc_connection.py

    private fun getPythonInstance(context: Context): Python {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(context))
        }
        return Python.getInstance()
    }

    fun createTransaction(context: Context,privateKey: String, publicKey:String, destinationPublicKey:String, amount:Float):String{
        return getPythonInstance(context)
            .getModule(transactionsModule)
            .callAttr("create_transaction",privateKey,publicKey,destinationPublicKey,amount)
            .toString()
    }

    fun getBalance(context: Context):String{
        val keyManager = KeyManager.getInstance()
        val publicKey = keyManager.getPublicKey(context)
        return getPythonInstance(context)
            .getModule(blockchainConnectionModule)
            .callAttr("get_balance_by_public_key",publicKey)
            .toString()
    }

    fun sendTransaction(context: Context,transaction: String): Boolean{
        return getPythonInstance(context)
            .getModule(blockchainConnectionModule)
            .callAttr("send_transaction",transaction)
            .toBoolean()
    }
}