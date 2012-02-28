package
{
	import Elixys.Assets.*;
	import Elixys.Components.*;
	import Elixys.Events.*;
	import Elixys.Extended.*;
	import Elixys.HTTP.*;
	import Elixys.JSON.*;
	import Elixys.JSON.State.*;
	import Elixys.Views.*;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Loader;
	import flash.display.Sprite;
	import flash.display.StageAlign;
	import flash.display.StageScaleMode;
	import flash.events.Event;
	import flash.events.EventDispatcher;
	import flash.events.HTTPStatusEvent;
	import flash.events.SoftKeyboardEvent;
	import flash.events.TimerEvent;
	import flash.net.SharedObject;
	import flash.net.URLLoader;
	import flash.net.URLRequest;
	import flash.text.Font;
	import flash.text.StyleSheet;
	import flash.text.TextFieldAutoSize;
	import flash.text.TextFormat;
	import flash.utils.*;
	
	// This is the root sprite for the Elixys application
	public class Elixys extends Sprite
	{
		/***
		 * Construction
		 **/
		
		public function Elixys(screen:Sprite = null)
		{
			// Add ourselves to the screen
			if (screen)
			{
				screen.addChild(this);
			}
			
			// Set the state alignment and scaling mode
			stage.align = StageAlign.TOP_LEFT;
			stage.scaleMode = StageScaleMode.NO_SCALE;

			// Crank up the frame rate
			stage.frameRate = 60;
			
			// Create the initial UI
			ElixysUI.Initialize();
			UI.create(this, PAGES, stage.stageWidth, stage.stageHeight);
			m_pPages = UIPages(UI.findViewById("Pages"));
			
			// Get a reference to the loading view and inform it that creation is complete
			m_pLoading = Loading(UI.findViewById("Loading"));
			m_pLoading.addEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnLoadingStartedTransitionComplete);
			m_pLoading.InitialDisplay();
			
			// Create the HTTP connection pool
			m_pHTTPConnectionPool = new HTTPConnectionPool(5);
			m_pHTTPConnectionPool.addEventListener(HTTPStatusEvent.HTTP_STATUS, OnHTTPStatusEvent);
			m_pHTTPConnectionPool.addEventListener(ExceptionEvent.EXCEPTION, OnHTTPExceptionEvent);
			
			// Add event listeners
			addEventListener(HTTPRequestEvent.HTTPREQUEST, OnHTTPRequest);
			addEventListener(ElixysEvents.LOGOUT, OnLogOut);
		}
		
		/***
		 * Loading functions
		 **/
		
		// Called when the loading started transition completes
		protected function OnLoadingStartedTransitionComplete(event:TransitionCompleteEvent):void
		{
			// Remove the event listener
			m_pLoading.removeEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnLoadingStartedTransitionComplete);
			
			// Iterate over our screens and count the number of loading steps
			m_nTotalLoadSteps = m_pScreenClasses.length;
			for (var nIndex:uint = 0; nIndex < m_pScreenClasses.length; ++nIndex)
			{
				var pClass:Class = m_pScreenClasses[nIndex];
				if (pClass["LOAD_STEPS"] != null)
				{
					m_nTotalLoadSteps += pClass["LOAD_STEPS"];
				}
			}
			m_nCurrentLoadStep = 0;
			
			// Create the loading timer
			m_pLoadTimer = new Timer(30, 1);
			m_pLoadTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnLoadTimerComplete);
			
			// Kick off the loading process
			LoadNext();
		}
		
		// Loads the next step
		protected function LoadNext():void
		{
			// Update the progress bar
			m_pLoading.SetProgress(m_nCurrentLoadStep / m_nTotalLoadSteps);
			
			// Start a timer before we load the next component.  This gives the main thread a chance to update the UI
			m_pLoadTimer.start();
		}
		
		// Called when the load timer completes
		protected function OnLoadTimerComplete(event:TimerEvent):void
		{
			// Iterate through our classes until we find something to load
			var nIndex:uint = 0;
			while (nIndex < m_pScreens.length)
			{
				// Ask this class to load the next step
				var pScreen:Screen = m_pScreens[nIndex] as Screen;
				if (pScreen.LoadNext())
				{
					// The next step has loaded
					++m_nCurrentLoadStep;
					LoadNext();
					return;
				}
				else
				{
					// This screen has nothing more to load
					++nIndex;
				}
			}
			
			// Create the next screen
			if (nIndex < m_pScreenClasses.length)
			{
				// Create the screen class
				var pAttributes:Attributes = new Attributes(0, 0, width, height);
				var pNextScreen:Form = new m_pScreenClasses[nIndex](this, this, new XML(), pAttributes);
				m_pScreens.push(pNextScreen);
				
				// Append the screen to the page list
				var pPages:Array = m_pPages.pages;
				pPages.push(pNextScreen);
				m_pPages.attachPages(pPages);
				m_pPages.xml.appendChild(pNextScreen.xml);

				// Update the layout
				m_pPages.layout(m_pPages.attributes);

				// The next screen has been loaded
				++m_nCurrentLoadStep;
				LoadNext();
				return;
			}
			
			// Loading is complete.  Set our references to the various pages
			m_pLogin = m_pScreens[LOGIN_INDEX - 1];
			m_pHome = m_pScreens[HOME_INDEX - 1];
			m_pSelectSaved = m_pScreens[SELECTSAVED_INDEX - 1];
			m_pSelectHistory = m_pScreens[SELECTHISTORY_INDEX - 1];
			
			// Inform the loading screen and wait until the transition completes
			m_pLoading.addEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnLoadingFinishedTransitionComplete);
			m_pLoading.LoadComplete();
		}
		
		// Called when the loading finished transition completes
		protected function OnLoadingFinishedTransitionComplete(event:TransitionCompleteEvent):void
		{
			// Remove the event listener
			m_pLoading.removeEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnLoadingFinishedTransitionComplete);
			
			// Switch to the login screen
			m_pPages.goToPage(LOGIN_INDEX);
			m_pLogin.InitialDisplay();
		}
		
		/***
		 * Soft keyboard functions
		 **/
		
		// Called to pan the entire application when the keyboard is raised or lowered
		public function PanApplication(nInputAreaOfInterestTop:int, nInputAreaOfInterestBottom:int):void
		{
			// Calculate the offset
			var nOffset:int = 0;
			if (stage.softKeyboardRect.y != 0)
			{
				// Center the area of interest
				var nAreaOfInterestCenter:int = (nInputAreaOfInterestTop + nInputAreaOfInterestBottom) / 2; 
				var nAvailableCenter:int = stage.softKeyboardRect.y / 2;
				if ((nAreaOfInterestCenter - nAvailableCenter) < stage.softKeyboardRect.height)
				{
					nOffset = nAvailableCenter - nAreaOfInterestCenter;
				}
				else
				{
					nOffset = -stage.softKeyboardRect.height;
				}
			}
			
			// Check if the desired offset has changed
			if (m_nPanOffset != nOffset)
			{
				// Create or reset the pan transition timer
				if (m_pPanTimer == null)
				{
					var nPanSteps:uint = 150 / TRANSITION_UPDATE_INTERVAL;
					m_pPanTimer = new Timer(TRANSITION_UPDATE_INTERVAL, nPanSteps);
					m_pPanTimer.addEventListener(TimerEvent.TIMER, OnPanTransitionTimer);
					m_pPanTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnPanTransitionTimerComplete);
				}
				else
				{
					m_pPanTimer.reset();
				}
				
				// Start a new pan transition
				m_nPanOffset = nOffset;
				m_nPanStep = (y - nOffset) / m_pPanTimer.repeatCount;
				m_pPanTimer.start();
			}
		}
		
		// Called once for each step in the pan transition
		protected function OnPanTransitionTimer(event:TimerEvent):void
		{
			y -= m_nPanStep;
		}
		
		// Called when the pan transition is complete
		protected function OnPanTransitionTimerComplete(event:TimerEvent):void
		{
			y = m_nPanOffset;
		}
		
		/***
		 * Error functions
		 **/
		
		// Called when the status of the HTTP request is know
		protected function OnHTTPStatusEvent(event:HTTPStatusEvent):void
		{
			// Catch any HTTP errors
			if (event.status != 200)
			{
				// Display the error
				if (event.status == 401)
				{
					ShowLoginScreen("Invalid username or password");
				}
				else
				{
					ShowLoginScreen("HTTP request failed (" + event.status + ")");
				}
			}
		}
		
		// Called when an exception occurs in the HTTP connection
		protected function OnHTTPExceptionEvent(event:ExceptionEvent):void
		{
			// Display the error
			ShowLoginScreen("HTTP exception (" + event.exception + ")");
		}
		
		// Catch all unhandled exceptions

		/***
		 * Connect to server functions
		 **/
		
		// Creates a connection to the server
		public function ConnectToServer(sServer:String, sUsername:String, sPassword:String):void
		{
			// Drop all existing connection
			m_pHTTPConnectionPool.DropAllConnections();
			
			// Set the server and credentials
			m_pHTTPConnectionPool.Server = sServer;
			m_pHTTPConnectionPool.SetRawCredentials(sUsername, sPassword);
			
			// Remove any HTTP response listeners
			m_pHTTPConnectionPool.removeEventListener(HTTPResponseEvent.HTTPRESPONSE, OnHTTPResponseEvent);
			m_pHTTPConnectionPool.removeEventListener(HTTPResponseEvent.HTTPRESPONSE, OnConnectionHTTPResponseEvent_Configuration);
			m_pHTTPConnectionPool.removeEventListener(HTTPResponseEvent.HTTPRESPONSE, OnConnectionHTTPResponseEvent_State);
			
			// Set the HTTP response listener
			m_pHTTPConnectionPool.addEventListener(HTTPResponseEvent.HTTPRESPONSE, OnConnectionHTTPResponseEvent_Configuration);
			
			// Load the system configuration
			m_pHTTPConnectionPool.SendRequestA("GET", "/Elixys/configuration", HTTPConnectionPool.MIME_JSON);
			
			// Start the connecting timer
		}
		
		// Called if the connecting timer goes off before we establish a connection to the server
		
		// Called when the configuration HTTP response is received
		protected function OnConnectionHTTPResponseEvent_Configuration(event:HTTPResponseEvent):void
		{
			// Ignore failed responses
			if (event.m_pHTTPResponse.m_nStatusCode != 200)
			{
				return;
			}
			
			// Load the configuration
			try
			{
				m_pConfiguration = ParseHTTPResponse(event, getQualifiedClassName(Configuration)) as Configuration;
			}
			catch (err:Error)
			{
				// Handle error
			}
			
			// Set the HTTP response listener
			m_pHTTPConnectionPool.removeEventListener(HTTPResponseEvent.HTTPRESPONSE, OnConnectionHTTPResponseEvent_Configuration);
			m_pHTTPConnectionPool.addEventListener(HTTPResponseEvent.HTTPRESPONSE, OnConnectionHTTPResponseEvent_State);
			
			// Load the system state
			m_pHTTPConnectionPool.SendRequestA("GET", "/Elixys/state", HTTPConnectionPool.MIME_JSON);
		}
		
		// Called when the state HTTP response is received
		protected function OnConnectionHTTPResponseEvent_State(event:HTTPResponseEvent):void
		{
			// Stop the connecting timer
			
			// Close the connecting popup if it is visible
			
			// Load the state
			try
			{
				m_pState = ParseHTTPResponse(event, getQualifiedClassName(State)) as State;
			}
			catch (err:Error)
			{
				// Handle error
			}
			
			// Set the HTTP response listener
			m_pHTTPConnectionPool.removeEventListener(HTTPResponseEvent.HTTPRESPONSE, OnConnectionHTTPResponseEvent_State);
			m_pHTTPConnectionPool.addEventListener(HTTPResponseEvent.HTTPRESPONSE, OnHTTPResponseEvent);
			
			// Fade out the login screen
			m_pLogin.addEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnLoginFadeTransitionComplete);
			m_pLogin.Fade(1, 0, 350);
		}
		
		// Called when the login screen has faded out
		protected function OnLoginFadeTransitionComplete(event:TransitionCompleteEvent):void
		{
			// Remove the event listener
			m_pLogin.removeEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnLoginFadeTransitionComplete);
			
			// Show the current screen
			UpdateState();
			
			// Start the state update timer
			if (m_pUpdateTimer == null)
			{
				m_pUpdateTimer = new Timer(500);
				m_pUpdateTimer.addEventListener(TimerEvent.TIMER, OnUpdateTimer);
			}
			m_pUpdateTimer.start();
		}

		/***
		 * Disconnect from server functions
		 **/
		
		// Called to terminate the connection to the server
		protected function OnLogOut(event:Event):void
		{
			ShowLoginScreen("");
		}
		
		// Show the log in screen with optional error message
		protected function ShowLoginScreen(sError:String):void
		{
			// Stop the state update timer
			if ((m_pUpdateTimer != null) && (m_pUpdateTimer.running))
			{
				m_pUpdateTimer.stop();
			}
			
			// Set the error text
			m_pLogin.SetError(sError);
			
			// Show the login screen
			m_pPages.goToPage(LOGIN_INDEX);
			if (m_pLogin.alpha != 1)
			{
				m_pLogin.Fade(0, 1, 350);
			}
		}

		
		/***
		 * Server communication functions
		 **/
		
		// Called to update the client state
		protected function OnUpdateTimer(event:TimerEvent):void
		{
			// Load the system state
			m_pHTTPConnectionPool.SendRequestA("GET", "/Elixys/state", HTTPConnectionPool.MIME_JSON);
		}

		// Called when a screen wants to send something to the server
		protected function OnHTTPRequest(event:HTTPRequestEvent):void
		{
			// Send the request to the server
			m_pHTTPConnectionPool.SendRequestB(event.m_pHTTPRequest);
		}
		
		// Called when an HTTP response is received
		protected function OnHTTPResponseEvent(event:HTTPResponseEvent):void
		{
			try
			{
				// Parse the response
				var pResponse:* = ParseHTTPResponse(event, getQualifiedClassName(State));
				
				// Call the appropriate update function
				if (pResponse is State)
				{
					m_pState = pResponse as State;
					UpdateState();
				}
				else
				{
					trace("handle other response types");
				}
			}
			catch (err:Error)
			{
				// Handle error
			}
		}
		
		// Parses the HTTP response
		protected function ParseHTTPResponse(event:HTTPResponseEvent, sClassName:String = ""):JSONObject
		{
			try
			{
				// Read in the contents of the response as a string
				var nReponseLength:uint = event.m_pHTTPResponse.m_pBody.length;
				var sResponse:String = event.m_pHTTPResponse.m_pBody.readUTFBytes(nReponseLength);
				
				// Parse the response as JSON
				var pJSON:JSONObject = new JSONObject(sResponse);
				
				// Find the object in our array
				for (var i:uint = 0; i < m_pJSONObjects.length; ++i)
				{
					if (pJSON.type == m_pJSONObjects[i].TYPE)
					{
						// Make sure this is the object we're looking for
						if ((sClassName != "") && (sClassName != getQualifiedClassName(m_pJSONObjects[i])))
						{
							continue;
						}
						
						// Create and return the object
						return new m_pJSONObjects[i](null, pJSON);
					}
				}
			}
			catch (err:Error)
			{
				trace(err);
			}
			return null;
		}
		
		/***
		 * Update functions
		 **/
		
		// Update the current state
		protected function UpdateState():void
		{
			// Handle the pop up window first
			if (m_pState.ClientState.PromptState.Show)
			{
				trace("Show popup");
				/*
				// Create and display the pop up window
				if (_viewPrompt == null)
				{
					_viewPrompt = new PromptView();
					_viewPrompt.addEventListener(HTTPRequestEvent.HTTPREQUEST, OnHTTPRequestEvent);
					PopUpManager.addPopUp(_viewPrompt, this, true);
				}
				
				// Update the pop up state
				_viewPrompt.UpdateState(pState);
				PopUpManager.centerPopUp(_viewPrompt);
				*/
			}
			/*
			else if (_viewPrompt != null)
			{
				// Remove the pop up window
				PopUpManager.removePopUp(_viewPrompt);
				_viewPrompt = null;
			}
			*/
			
			// Determine the screen we should be showing
			var nPageIndex:uint;
			var pScreen:Screen;
			if (m_pState.ClientState.Screen == StateHome.TYPE)
			{
				nPageIndex = HOME_INDEX;
				pScreen = m_pHome;
			}
			else if (m_pState.ClientState.Screen == StateSelectSaved.TYPE)
			{
				nPageIndex = SELECTSAVED_INDEX;
				pScreen = m_pSelectSaved;
			}
			else if (m_pState.ClientState.Screen == StateSelectHistory.TYPE)
			{
				nPageIndex = SELECTHISTORY_INDEX;
				pScreen = m_pSelectHistory;
			}
			else if (StateSequence.CheckState(m_pState.ClientState.Screen))
			{
				nPageIndex = SEQUENCE_INDEX;
			}
			else
			{
				trace("Unknown client state received from server: " + m_pState.ClientState.Screen);
			}

			// Update the target screen
			pScreen.UpdateState(m_pState);

			// Check if the screen has changed
			if (nPageIndex != m_pPages.pageNumber)
			{
				// Show the new screen
				m_pPages.goToPage(nPageIndex);
			}
		}

		/***
		 * Member variables
		 **/
		
		// XML page list
		protected static const PAGES:XML = 
			<pages id="Pages" alignV="fill" alignH="fill">
				<loading id="Loading" border="false" alignV="fill" alignH="fill"/>
			</pages>;
		
		// Pages
		protected var m_pPages:UIPages;
		
		// Loading variables
		protected var m_pLoading:Loading;
		protected var m_pLoadTimer:Timer;
		protected var m_nTotalLoadSteps:uint;
		protected var m_nCurrentLoadStep:uint;
		
		// Update variables
		protected var m_pUpdateTimer:Timer;
		
		// Screen variables
		protected var m_pScreenClasses:Array = [Login, Home, SelectSaved, SelectHistory, Sequence];
		protected var m_pScreens:Array = new Array;
		protected var m_pLogin:Login;
		protected var m_pHome:Home;
		protected var m_pSelectSaved:SelectSaved;
		protected var m_pSelectHistory:SelectHistory;
		
		// Transition update interval (milliseonds)
		public static var TRANSITION_UPDATE_INTERVAL:uint = 20;
		
		// Constants to refer to the page indicies (one-based because of loading page)
		protected static var LOGIN_INDEX:uint = 1;
		protected static var HOME_INDEX:uint = 2;
		protected static var SELECTSAVED_INDEX:uint = 3;
		protected static var SELECTHISTORY_INDEX:uint = 4;
		protected static var SEQUENCE_INDEX:uint = 5;
		
		// Pan transition variables
		protected var m_nPanStep:Number = 0;
		protected var m_nPanOffset:Number = 0;
		protected var m_pPanTimer:Timer;
		
		// HTTP connection pool
		protected var m_pHTTPConnectionPool:HTTPConnectionPool;
		
		// Server configuration and move recent client state
		protected var m_pConfiguration:Configuration;
		protected var m_pState:State;
		
		// Array of recognized JSON objects
		protected static var m_pJSONObjects:Array = [Configuration, State];
		
		// Unused reference to our static assets that is required for them to be available at run time
		protected var m_pAssets:StaticAssets;
	}
}
