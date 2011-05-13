package Elixys
{
	import com.hurlant.crypto.tls.*;
	
	import flash.events.Event;
	import flash.events.EventDispatcher;
	import flash.events.HTTPStatusEvent;
	import flash.events.IOErrorEvent;
	import flash.events.ProgressEvent;
	import flash.events.SecurityErrorEvent;
	import flash.net.Socket;
	import flash.utils.ByteArray;
	
	import mx.utils.Base64Encoder;

	// This class performs normal HTTP operations over a socket.  Yes, it's lame that we need to implement this.  It should
	// be part of Adobe's library, but their version is severly limited in terms of functionality.
	public class HTTPConnection extends EventDispatcher
	{
		/***
		 * Public functions
		 **/
		
		// Constructor
		public function HTTPConnection(sClientIP:String)
		{
			// Remember the client IP
			m_sClientIP = sClientIP;
		}
		
		// Sets the user's credentials
		public function SetCredentials(sUsername:String, sPassword:String):void
		{
			// Remember credentials
			m_sUsername = sUsername;
			m_sPassword = sPassword;
		}

		// Connects to the given server and port
		public function Connect(sServer:String, nPort:uint):void
		{
			// Remember server and port
			m_sServer = sServer;
			m_nPort = nPort;
	
			// Determine if we are using encryption
			if (nPort != 443)
			{
				// No, so create a normal socket
				m_pSocket = new Socket();
				m_pSocket.addEventListener(Event.CONNECT, OnSocketConnectEvent);
				m_pSocket.addEventListener(ProgressEvent.SOCKET_DATA, OnSocketProgressEvent);
				m_pSocket.addEventListener(IOErrorEvent.IO_ERROR, OnSocketIOErrorEvent);
				m_pSocket.addEventListener(SecurityErrorEvent.SECURITY_ERROR, OnSocketSecurityErrorEvent);
					
				// Connect to the remote server
				m_pSocket.connect(m_sServer, m_nPort);
			}
			else
			{
				// Yes, so create a TLS socket
				var pTLSConfig:TLSConfig = new TLSConfig(TLSEngine.CLIENT);
				pTLSConfig.trustAllCertificates = true;
				pTLSConfig.ignoreCommonNameMismatch = true;
				m_pTLSSocket = new TLSSocket(m_sServer, m_nPort, pTLSConfig);
				m_pTLSSocket.addEventListener(Event.CONNECT, OnSocketConnectEvent);
				m_pTLSSocket.addEventListener(ProgressEvent.SOCKET_DATA, OnSocketProgressEvent);
				m_pTLSSocket.addEventListener(IOErrorEvent.IO_ERROR, OnSocketIOErrorEvent);
				m_pTLSSocket.addEventListener(SecurityErrorEvent.SECURITY_ERROR, OnSocketSecurityErrorEvent);
	
				// Connect to the remote server
				m_pTLSSocket.connect(m_sServer, m_nPort);
			}
		}

		public function SendRequest(sOperation:String, sResource:String, sAcceptMIME:String, pHeaders:Array = null, pBody:ByteArray = null,
			sBodyMIME:String = ""):void
		{
			// Encode the username and password
			var pEncoder:Base64Encoder = new Base64Encoder();
			pEncoder.insertNewLines = false;
			pEncoder.encode(m_sUsername + ":" + m_sPassword);
			
			var sRequest:String = "GET " + sResource + " HTTP/1.1\r\n" +
				"Host: " + m_sClientIP + "\r\n" +
				"User-Agent: AdobeAIR\r\n" +
				"Accept: " + sAcceptMIME + "\r\n" +
				"Authorization: Basic " + pEncoder.toString() + "\r\n" +
				//"Content-Type: application/x-www-form-urlencoded\r\n" +
				"Connection: Keep-Alive\r\n\r\n";

			for (var i:uint = 0; i < sRequest.length; ++i)
			{
				m_pTLSSocket.writeByte(sRequest.charCodeAt(i));
			}
			m_pTLSSocket.flush();
		}

		// Returns the HTTP response
		public function GetResponseStatus():uint
		{
			return m_nStatusCode;
		}
		public function GetResponseHeaders():Array
		{
			return m_pHTTPResponseHeaders;
		}
		public function GetResponseBody():ByteArray
		{
			return m_pHTTPResponseBody;
		}

		/***
		 * Message handlers
		 ***/
		
		// Called when the socket is connected
		private function OnSocketConnectEvent(event:Event):void
		{
			// Check our connected flag to make sure we only dispatch this event once
			if (!m_bConnected)
			{
				// Pass the connection even to anyone listening
				dispatchEvent(event);
				
				// Set the flag
				m_bConnected = true;
			}
		}
		
		// Called as the socket receives data
		private function OnSocketProgressEvent(event:ProgressEvent):void
		{
			try
			{
				// Make sure we have data available
				if (!m_pTLSSocket.bytesAvailable)
				{
					return;
				}
				
				// Capture the HTTP response headers if we don't have them yet
				if (!m_nContentLength)
				{
					do
					{
						// Add the next byte to the header
						var nByte:uint = m_pTLSSocket.readByte();
						m_pHTTPResponseHeader.writeByte(nByte);
						
						// Watch for the terminating sequence
						var nNextHeaderByte:uint;
						if ((m_nHTTPResponseHeader == 0) || (m_nHTTPResponseHeader == 2))
						{
							nNextHeaderByte = 0xD;
						}
						else
						{
							nNextHeaderByte = 0xA;
						}
						if (nByte == nNextHeaderByte)
						{
							++m_nHTTPResponseHeader;
						}
						else
						{
							m_nHTTPResponseHeader = 0;
						}
					} while ((m_nHTTPResponseHeader != 4) && m_pTLSSocket.bytesAvailable);
					
					// Now we have the HTTP response header.  Break the byte array into an array of strings
					m_pHTTPResponseHeaders = m_pHTTPResponseHeader.toString().split("\r\n");
					
					// Extract the status code and content length
					m_nStatusCode = ExtractStatusCode();
					m_nContentLength = ExtractContentLength();
	
					// Inform anyone listening of the status code
					var pHTTPStatusEvent:HTTPStatusEvent = new HTTPStatusEvent(HTTPStatusEvent.HTTP_STATUS, false, false, m_nStatusCode);
					dispatchEvent(pHTTPStatusEvent);
				}
			
				// Continue adding the new bytes to the body until we have it all
				if ((m_nContentLength - m_pHTTPResponseBody.bytesAvailable) > m_pTLSSocket.bytesAvailable)
				{
					m_pTLSSocket.readBytes(m_pHTTPResponseBody, m_pHTTPResponseBody.bytesAvailable, m_pTLSSocket.bytesAvailable);
				}
				else
				{
					m_pTLSSocket.readBytes(m_pHTTPResponseBody, m_pHTTPResponseBody.bytesAvailable, m_nContentLength - m_pHTTPResponseBody.bytesAvailable);
				}
	
				// Inform anyone listening of our progress
				var pProgressEvent:ProgressEvent = new ProgressEvent(ProgressEvent.PROGRESS, false, false, m_pHTTPResponseBody.bytesAvailable,
					m_nContentLength);
				dispatchEvent(pProgressEvent);
			}
			catch (err:Error)
			{
				var pExceptionEvent:ExceptionEvent = new ExceptionEvent("Error when receiving socket data: " + err.message);
				dispatchEvent(pExceptionEvent);
			}
		}

		// Called when a socket IO or security error occurs
		private function OnSocketIOErrorEvent(event:IOErrorEvent):void
		{
			var pExceptionEvent:ExceptionEvent = new ExceptionEvent("Socket IO error: " + event.text);
			dispatchEvent(pExceptionEvent);
		}		
		private function OnSocketSecurityErrorEvent(event:SecurityErrorEvent):void
		{
			var pExceptionEvent:ExceptionEvent = new ExceptionEvent("Socket security error: " + event.text);
			dispatchEvent(pExceptionEvent);
		}

		/***
		 * Private functions
		 **/

		// Extract status code from the HTTP response headers
		private function ExtractStatusCode():uint
		{
			// Scan for the HTTP status code
			for each (var sHeader:String in m_pHTTPResponseHeaders)
			{
				if (sHeader.slice(0, HTTP_STATUS.length) == HTTP_STATUS)
				{
					// Found it.  Extract the code
					return int(sHeader.slice(HTTP_STATUS.length, HTTP_STATUS.length + 3));
				}
			}
			
			// Failed to find HTTP status code
			throw new Error("Corrupt HTTP response");
		}
		
		// Extract content length from the HTTP response headers
		private function ExtractContentLength():uint
		{
			// Scan for the HTTP content length
			for each (var sHeader:String in m_pHTTPResponseHeaders)
			{
				if (sHeader.slice(0, HTTP_CONTENTLENGTH.length) == HTTP_CONTENTLENGTH)
				{
					// Found it.  Extract the content length
					return int(sHeader.slice(HTTP_CONTENTLENGTH.length));
				}
			}
			
			// Failed to find HTTP content length
			throw new Error("Corrupt HTTP response");
		}
		
		/***
		 * Data members
		 **/
		
		// Client IP
		private var m_sClientIP:String = "";
		
		// Server and port
		private var m_sServer:String = "";
		private var m_nPort:uint = 0;
		
		// User credentials
		private var m_sUsername:String = "";
		private var m_sPassword:String = "";
		
		// Socket classes
		private var m_pSocket:Socket = null;
		private var m_pTLSSocket:TLSSocket = null;
		private var m_bConnected:Boolean = false;

		// HTTP response
		private var m_pHTTPResponseHeader:ByteArray = new ByteArray();
		private var m_nHTTPResponseHeader:uint = 0;
		private var m_pHTTPResponseHeaders:Array = null;
		private var m_nStatusCode:uint = 0;
		private var m_nContentLength:uint = 0;
		private var m_pHTTPResponseBody:ByteArray = new ByteArray();

		// Static MIME strings
		public static var MIME_FLASH:String = "application/x-shockwave-flash";
		public static var MIME_JSON:String = "application/json";
			
		// Static HTTP strings
		private static var HTTP_STATUS:String = "HTTP/1.1 ";
		private static var HTTP_CONTENTLENGTH:String = "Content-Length: ";
	}
}
