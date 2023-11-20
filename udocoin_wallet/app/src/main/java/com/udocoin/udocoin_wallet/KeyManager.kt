package com.udocoin.udocoin_wallet

import android.content.Context
import android.util.Log
import android.widget.Toast
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class KeyManager() {

    private val TAG = "[KEY GENERATOR]"

    companion object {
        private var instance:KeyManager? = null
        fun getInstance(): KeyManager = instance ?: synchronized(this){
            instance ?:KeyManager().also { instance = it }
        }
    }

    private val keyManagerModule = "key_manager" // key_manager.py
    private val transactionsModule = "transactions" // transactions.py

    private fun getPythonInstance(context: Context): Python {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(context))
        }
        return Python.getInstance()
    }

    fun hasValidKeys(context: Context):Boolean{
        return getPythonInstance(context).getModule(keyManagerModule).callAttr("has_valid_keys").toBoolean()
    }


    fun generateNewKeyPair(context: Context){
        getPythonInstance(context).getModule(keyManagerModule).callAttr("generate_and_safe_new_key_pair")
    }

    fun saveKeys(context: Context, privateKey: String, publicKey: String){

    }

    private fun getKey(context:Context,func:String):String?{
        val key = getPythonInstance(context).getModule(keyManagerModule).callAttr(func).toString()
        return if (key == "") null else key
    }

    fun getPrivateKey(context: Context): String? {
        return getKey(context,"get_private_key_from_file_string")
    }

    fun getPublicKey(context: Context): String? {
        return getKey(context,"get_public_key_from_file_string")
    }

    fun getPublicKeyFromPrivateKey(context:Context, privateKey: String):String?{
        if(!isValidPrivateKey(context,privateKey)){
            return null
        }
        return getPythonInstance(context)
            .getModule(keyManagerModule)
            .callAttr("generate_public_key_from_private_key_string",privateKey)
            .toString()
    }

    fun setPrivateKey(context: Context,privateKey: String){
        getPythonInstance(context)
            .getModule(keyManagerModule)
            .callAttr("safe_private_key_to_file_string",privateKey)
    }

    fun setPublicKey(context: Context,publicKey: String){
        getPythonInstance(context)
            .getModule(keyManagerModule)
            .callAttr("safe_public_key_to_file_string",publicKey)
    }

    fun isValidPrivateKey(context: Context, privateKey:String):Boolean{
        return getPythonInstance(context)
            .getModule(keyManagerModule)
            .callAttr("is_valid_private_key_string",privateKey)
            .toBoolean()
    }

    fun isValidPublicKey(context: Context, publicKey: String):Boolean{
        //TODO python validate public key function
        return true
    }

    fun isValidKeyPair(context: Context, publicKey:String, privateKey:String):Boolean{
        return getPythonInstance(context)
            .getModule(keyManagerModule)
            .callAttr("is_valid_key_pair_strings",privateKey,publicKey)
            .toBoolean()
    }
}