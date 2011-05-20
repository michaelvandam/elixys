package Elixys.HTTP
{
	import Elixys.Events.ExceptionEvent;
	import Elixys.Events.HTTPResponseEvent;
	
	import flash.events.Event;
	import flash.events.EventDispatcher;
	import flash.events.HTTPStatusEvent;
	import flash.events.IOErrorEvent;
	import flash.events.ProgressEvent;
	import flash.events.SecurityErrorEvent;
	import flash.events.TimerEvent;
	import flash.net.Socket;
	import flash.utils.ByteArray;
	import flash.utils.Dictionary;
	import flash.utils.Timer;
	
	import mx.collections.ArrayList;
	import mx.controls.Alert;
	import mx.utils.Base64Encoder;

	// This class performs normal HTTP operations over a socket.  Yes, it's lame that we need to implement this.  It should
	// be part of Adobe's library, but their version is severly limited in terms of functionality.
	public class HTTPConnection extends EventDispatcher
	{
		/***
		 * Public functions
		 **/
		
		// Constructor
		public function HTTPConnection()
		{
			// Add event listeners
			m_pResponseTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnResponseTimerComplete);
		}
		
		// Set and get the user's credentials
		public function SetCredentials1(sUsername:String, sPassword:String):void
		{
			// Encode the username and password using basic authentication
			var pEncoder:Base64Encoder = new Base64Encoder();
			pEncoder.insertNewLines = false;
			pEncoder.encode(sUsername + ":" + sPassword);
			m_sCredentials = pEncoder.toString();
		}
		public function SetCredentials2(sCredentials:String):void
		{
			// Remember the credentials
			m_sCredentials = sCredentials;
		}
		public function GetCredentials():String
		{
			// Return the credentials that we have
			return m_sCredentials;
		}

		// Connects to the given server and port
		public function Connect(sServer:String, nPort:uint):void
		{
			// Remember server and port
			m_sServer = sServer;
			m_nPort = nPort;
	
			// Create a new socket and add event listener
			m_pSocket = new Socket();
			m_pSocket.addEventListener(Event.CONNECT, OnSocketConnectEvent);
			m_pSocket.addEventListener(ProgressEvent.SOCKET_DATA, OnSocketProgressEvent);
			m_pSocket.addEventListener(IOErrorEvent.IO_ERROR, OnSocketIOErrorEvent);
			m_pSocket.addEventListener(SecurityErrorEvent.SECURITY_ERROR, OnSocketSecurityErrorEvent);
					
			// Connect to the remote server
			m_pSocket.connect(m_sServer, m_nPort);
		}

		public function SendRequest(sMethod:String, sResource:String, sAcceptMIME:String, pHeaders:Array = null, pBody:ByteArray = null):void
		{
			// Wrap the parameters in an HTTPRequest object
			var pHTTPRequest:HTTPRequest = new HTTPRequest();
			pHTTPRequest.m_sMethod = sMethod;
			pHTTPRequest.m_sResource = sResource;
			pHTTPRequest.m_sAcceptMIME = sAcceptMIME;
			pHTTPRequest.m_pHeaders = pHeaders;
			pHTTPRequest.m_pBody = pBody;
			
			// Make sure there is no outstanding request
			if (m_pOutstandingRequest != null)
			{
				// Store the request in our array so we can send it later
				m_pHTTPRequestQueue.addItem(pHTTPRequest);
				return;
			}

			// Reset our retry counter
			m_nRetryCount = 0;
			
			// Send the request
			SendRequestInternal(pHTTPRequest);			
		}

		/***
		 * Internal functions
		 **/
		
		private function SendRequestInternal(pHTTPRequest:HTTPRequest):void
		{
			try
			{
				// Remember the outstanding request
				m_pOutstandingRequest = pHTTPRequest;
				
				// Create our initial request headers
				var pHeaderArray:Array = new Array();
				pHeaderArray.push("Host: " + m_sServer);
				pHeaderArray.push("User-Agent: AdobeAIR");
				pHeaderArray.push("Accept: " + pHTTPRequest.m_sAcceptMIME);
				pHeaderArray.push("Authorization: Basic " + m_sCredentials);
				pHeaderArray.push("Connection: Keep-Alive");
				
				// Add post headers
				var sMethod:String = pHTTPRequest.m_sMethod.toUpperCase();
				if (sMethod == "POST")
				{
					if (pHTTPRequest.m_pBody != null)
					{
						pHeaderArray.push("Content-Length: " + pHTTPRequest.m_pBody.bytesAvailable);
					}
					else
					{
						pHeaderArray.push("Content-Length: 0");
					}
					pHeaderArray.push("Content-Type: " + MIME_JSON);
				}
				
				// Add the specified request headers
				if (pHTTPRequest.m_pHeaders != null)
				{
					pHeaderArray = pHTTPRequest.m_pHeaders.concat(pHeaderArray);
				}
				
				// Format the request string
				var sRequest:String = sMethod + " " + pHTTPRequest.m_sResource + " HTTP/1.1\r\n";
				sRequest += pHeaderArray.join("\r\n");
				sRequest += "\r\n\r\n";
				
				// Send the request
				for (var i:uint = 0; i < sRequest.length; ++i)
				{
					m_pSocket.writeByte(sRequest.charCodeAt(i));
				}
				
				// Send the body
				if (pHTTPRequest.m_pBody != null)
				{
					m_pSocket.writeBytes(pHTTPRequest.m_pBody);
				}
				
				// Flush the socket
				m_pSocket.flush();

				// Start the response timer
				m_pResponseTimer.start();
			}
			catch (err:Error)
			{
				// Check for invalid sockets
				if (err.errorID == 2002)
				{
					// This socket has gone bad.  Drop the connection and create a new one
					m_pSocket = null;
					m_bConnected = false;
					Connect(m_sServer, m_nPort);
				}
				else
				{
					// Pass an exception event up to our parent
					var pExceptionEvent:ExceptionEvent = new ExceptionEvent("Sending HTTP request failed: " + err.message);
					dispatchEvent(pExceptionEvent);
				}
			}
		}

		/***
		 * Message handlers
		 ***/
		
		// Called when the socket is connected
		private function OnSocketConnectEvent(event:Event):void
		{
			// Check our connected flag to make sure we only acknowledge this event once
			if (!m_bConnected)
			{
				// Are we sitting on an outstanding request?
				if (m_pOutstandingRequest != null)
				{
					// Yes, so send it
					SendRequestInternal(m_pOutstandingRequest);
				}
				else
				{
					// No, so dispatch the connection event to anyone listening
					dispatchEvent(event);
				}
				
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
				if (!m_pSocket.bytesAvailable)
				{
					return;
				}
				
				// Capture the HTTP response headers if we don't have them yet
				if (!m_nContentLength)
				{
					do
					{
						// Add the next byte to the header
						var nByte:uint = m_pSocket.readByte();
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
					} while ((m_nHTTPResponseHeader != 4) && m_pSocket.bytesAvailable);
					
					// Return if we don't have the entire header yet
					if (m_nHTTPResponseHeader != 4)
					{
						return;
					}
					
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
				if ((m_nContentLength - m_pHTTPResponseBody.bytesAvailable) > m_pSocket.bytesAvailable)
				{
					m_pSocket.readBytes(m_pHTTPResponseBody, m_pHTTPResponseBody.bytesAvailable, m_pSocket.bytesAvailable);
				}
				else
				{
					m_pSocket.readBytes(m_pHTTPResponseBody, m_pHTTPResponseBody.bytesAvailable, m_nContentLength - m_pHTTPResponseBody.bytesAvailable);
				}
	
				// Inform anyone listening of our progress
				var pProgressEvent:ProgressEvent = new ProgressEvent(ProgressEvent.PROGRESS, false, false, m_pHTTPResponseBody.bytesAvailable,
					m_nContentLength);
				dispatchEvent(pProgressEvent);
				
				// Is this request is complete?
				if (m_pHTTPResponseBody.length == m_nContentLength)
				{
					// Yes, so stop the timer
					m_pResponseTimer.stop();

					// Create and dispatch the response
					var pHTTPResponse:HTTPResponse = new HTTPResponse();
					pHTTPResponse.m_nStatusCode = m_nStatusCode;
					pHTTPResponse.m_pHeaders = m_pHTTPResponseHeaders;
					pHTTPResponse.m_pBody = m_pHTTPResponseBody;
					dispatchEvent(new HTTPResponseEvent(pHTTPResponse));

					// Reset our state
					m_pHTTPResponseHeader.clear();
					m_nHTTPResponseHeader = 0;
					m_pHTTPResponseHeaders = null;
					m_nStatusCode = 0;
					m_nContentLength = 0;
					m_pHTTPResponseBody.clear();
					m_pOutstandingRequest = null;
										
					// Submit the next request if one is in our queue
					if (m_pHTTPRequestQueue.length)
					{
						var pHTTPRequest:HTTPRequest = m_pHTTPRequestQueue.getItemAt(0) as HTTPRequest;
						m_pHTTPRequestQueue.removeItemAt(0);
						SendRequest(pHTTPRequest.m_sMethod, pHTTPRequest.m_sResource, pHTTPRequest.m_sAcceptMIME, pHTTPRequest.m_pHeaders,
							pHTTPRequest.m_pBody);
					}
				}
			}
			catch (err:Error)
			{
				var pExceptionEvent:ExceptionEvent = new ExceptionEvent("Error when receiving socket data: " + err.message);
				dispatchEvent(pExceptionEvent);
			}
		}

		// Called when the response timer completes
		private function OnResponseTimerComplete(event:TimerEvent):void
		{
			// Have we exceeded out retry limit?
			if (m_nRetryCount < 3)
			{
				// No, so increment our counter and reset our state
				++m_nRetryCount;
				m_pHTTPResponseHeader.clear();
				m_nHTTPResponseHeader = 0;
				m_pHTTPResponseHeaders = null;
				m_nStatusCode = 0;
				m_nContentLength = 0;
				m_pHTTPResponseBody.clear();

				// Send the failed request again
				SendRequestInternal(m_pOutstandingRequest);
			}
			else
			{
				// Give up and send an exception event
				var pExceptionEvent:ExceptionEvent = new ExceptionEvent("HTTP request timed out");
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
		
		// Server and port
		private var m_sServer:String = "";
		private var m_nPort:uint = 0;
		
		// User credentials
		private var m_sCredentials:String = "";
		
		// Socket classes
		private var m_pSocket:Socket = null;
		private var m_bConnected:Boolean = false;

		// HTTP response
		private var m_pHTTPResponseHeader:ByteArray = new ByteArray();
		private var m_nHTTPResponseHeader:uint = 0;
		private var m_pHTTPResponseHeaders:Array = null;
		private var m_nStatusCode:uint = 0;
		private var m_nContentLength:uint = 0;
		private var m_pHTTPResponseBody:ByteArray = new ByteArray();

		// Response timer, outstanding HTTP request and retry count
		private var m_pResponseTimer:Timer = new Timer(1000, 1);
		private var m_pOutstandingRequest:HTTPRequest;
		private var m_nRetryCount:uint;
		
		// HTTP request queue
		private var m_pHTTPRequestQueue:ArrayList = new ArrayList();
		
		// Static MIME strings
		public static var MIME_FLASH:String = "application/x-shockwave-flash";
		public static var MIME_JSON:String = "application/json";
		public static var MIME_HTML:String = "text/html";
			
		// Static HTTP strings
		private static var HTTP_STATUS:String = "HTTP/1.1 ";
		private static var HTTP_CONTENTLENGTH:String = "Content-Length: ";
	}
}
