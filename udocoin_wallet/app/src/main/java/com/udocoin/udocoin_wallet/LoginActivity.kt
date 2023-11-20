package com.udocoin.udocoin_wallet

import android.content.Intent
import android.net.Uri
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import java.io.BufferedReader
import java.io.File
import java.io.InputStreamReader
import java.security.PrivateKey

class LoginActivity : AppCompatActivity() {
    lateinit var keyManager: KeyManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)
        keyManager = KeyManager.getInstance()
        /** Go to main activity if keys are valid */
        if (keyManager.hasValidKeys(this)){
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
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
            if(fileContent == null){
                showFileChooser()
                return
            }
            if(!keyManager.isValidPrivateKey(this,fileContent)){
                Toast.makeText(this,"Invalid private key",Toast.LENGTH_SHORT).show()
                return
            }
            handlePrivateKeyUpload(fileContent)
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
            // Now 'fileContent' contains the content of the selected text file
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
        intent.putExtra("mode","loginScanner")
        startActivity(intent)
    }

    private fun generateNewKeys(){
        keyManager.generateNewKeyPair(this)
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
    }

    private fun handlePrivateKeyUpload(privateKey: String){
        if(!keyManager.isValidPrivateKey(this,privateKey)){
            Toast.makeText(this,"Invalid key.",Toast.LENGTH_SHORT).show()
            return
        }
        val publicKey = keyManager.getPublicKeyFromPrivateKey(this,privateKey)
        if(publicKey == null){
            Toast.makeText(this,"Error getting public key from private key.",Toast.LENGTH_SHORT).show()
            return
        }
        keyManager.setPrivateKey(this,privateKey)
        keyManager.setPublicKey(this,publicKey)

        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
    }
}