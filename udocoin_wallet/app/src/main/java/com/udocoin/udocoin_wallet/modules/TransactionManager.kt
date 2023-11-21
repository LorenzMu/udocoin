package com.udocoin.udocoin_wallet.modules

import android.content.Context
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class TransactionManager {
    companion object {
        private var instance: TransactionManager? = null
        fun getInstance(): TransactionManager = instance ?: synchronized(this){
            instance ?: TransactionManager().also { instance = it }
        }
    }

    private val transactionsModule = "transactions" // transactions.py

    private fun getPythonInstance(context: Context): Python {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(context))
        }
        return Python.getInstance()
    }

    fun createTransaction(context: Context,privateKey: String, publicKey:String, destinationPublicKey:String, amount:Float):Map<*,*>{
        return getPythonInstance(context)
            .getModule(transactionsModule)
            .callAttr("create_transaction",privateKey,publicKey,destinationPublicKey,amount)
            .toMap()
    }
}