package com.udocoin.udocoin_wallet

import android.content.Context
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class KeyManager() {
    companion object {
        private var instance:KeyManager? = null
        fun getInstance(): KeyManager = instance ?: synchronized(this){
            instance ?:KeyManager().also { instance = it }
        }
    }

    private val keyManagerModule = "key_manager"
    private val transactionsModule = "transactions"

    private fun getPythonInstance(context: Context): Python {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(context))
        }
        return Python.getInstance()
    }

    fun hasKeys(context: Context):Boolean{
        return getPythonInstance(context).getModule(keyManagerModule).callAttr("has_keys").toBoolean()
    }

    private fun getKey(context:Context,func:String):String?{
        val py = getPythonInstance(context)
        val module = py.getModule(keyManagerModule)
        val key = module.callAttr(func).toString()
        if(key == ""){
            return null
        }
        return key
    }

    fun getPrivateKey(context: Context): String? {
        return getKey(context,"get_private_key")
    }

    fun getPublicKey(context: Context): String? {
        return getKey(context,"get_public_key")
    }
}