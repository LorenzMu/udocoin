package com.udocoin.udocoin_wallet

import android.content.Intent
import android.net.Uri
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.Toast
import com.udocoin.udocoin_wallet.modules.KeyManager
import java.io.BufferedReader
import java.io.InputStreamReader

class LoginActivity : AppCompatActivity() {
    lateinit var keyManager: KeyManager
    val TAG = "[LOGIN ACTIVITY]"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)
        keyManager = KeyManager.getInstance()
        /** callback from scanner activity */
        val scanResult = intent.getStringExtra("scanResult")
        if(scanResult != null ){
            handlePrivateKeyUpload(scanResult)
        }
        /** Go to main activity if keys are valid */
        if (keyManager.hasValidKeys(this)){
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
            finish()
        }
        /** Stay at login activity if there are no keys or keys are invalid */
        findViewById<Button>(R.id.upload_button).setOnClickListener { showFileChooser() }
        findViewById<Button>(R.id.scan_button).setOnClickListener { goToScanner() }
        findViewById<Button>(R.id.generate_new_keys_button).setOnClickListener { generateNewKeys() }
    }

    private fun showFileChooser(){
        val intent = Intent(Intent.ACTION_GET_CONTENT)
        intent.type = "*/*"
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        try {
            startActivityForResult(Intent.createChooser(intent,"Select a file"),100)
        }catch (exception: java.lang.Exception){
            Toast.makeText(this, "Please install a file manager.", Toast.LENGTH_SHORT).show()
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if(requestCode == 100 && resultCode == RESULT_OK && data != null){
            val uri: Uri? = data.data
            val fileContent = uri?.let { readFileContent(it) }
            /** if unable to read */
            Log.d(TAG, "File Content: $fileContent")
            if(fileContent == null){
                showFileChooser()
                return
            }
            handlePrivateKeyUpload(fileContent)
            return
        }
        super.onActivityResult(requestCode, resultCode, data)
    }

    private fun readFileContent(uri: Uri):String? {
        try {
            val inputStream = contentResolver.openInputStream(uri)
            val reader = BufferedReader(InputStreamReader(inputStream))
            val stringBuilder = StringBuilder()
            var line: String?

            while (reader.readLine().also { line = it } != null) {
                stringBuilder.append(line).append("\n")
            }

            val fileContent = stringBuilder.toString()
            Toast.makeText(this, "File content: $fileContent", Toast.LENGTH_LONG).show()
            reader.close()
            inputStream?.close()
            return fileContent
        } catch (e: Exception) {
            Toast.makeText(this, "Error reading file content", Toast.LENGTH_SHORT).show()
        }
        return null
    }

    private fun goToScanner(){
        val intent = Intent(this, CodeScannerActivity::class.java)
        intent.putExtra("redirectActivity","LoginActivity")
        startActivity(intent)
    }

    private fun generateNewKeys(){
        keyManager.generateNewKeyPair(this)
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
    }

    private fun handlePrivateKeyUpload(privateKey: String){
        if(!keyManager.isValidPrivateKey(this,privateKey)){
            Toast.makeText(this,"Invalid private key.",Toast.LENGTH_SHORT).show()
            return
        }
        keyManager.setPrivateKey(this,privateKey)
        val publicKey = keyManager.setPublicKeyFromPrivateKey(this,privateKey)
        if(publicKey == null){
            Toast.makeText(this,"Error creating public key.",Toast.LENGTH_SHORT).show()
        }
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
        finish()
    }
}