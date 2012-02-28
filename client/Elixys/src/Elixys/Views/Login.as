package Elixys.Views
{
	import Elixys.Assets.Constants;
	import Elixys.Assets.Styling;
	import Elixys.Components.*;
	import Elixys.Events.*;
	import Elixys.Extended.*;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.InteractiveObject;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.KeyboardEvent;
	import flash.events.MouseEvent;
	import flash.events.SoftKeyboardEvent;
	import flash.events.TextEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.net.SharedObject;
	import flash.ui.Keyboard;
	import flash.utils.*;

	// This loading view is an extension of the Screen class
	public class Login extends Screen
	{
		/***
		 * Construction
		 **/
		
		public function Login(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, LOGIN_SCREEN, attributes, row, inGroup);
		}

		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public override function LoadNext():Boolean
		{
			if (m_nChildrenLoaded < LOAD_STEPS)
			{
				// Step 1 is loading the logo
				if (m_nChildrenLoaded == 0)
				{
					LoadLogo();
				}
				
				// Step 2 is loading the login
				if (m_nChildrenLoaded == 1)
				{
					LoadLogin();
				}
				
				// Increment and return
				++m_nChildrenLoaded;
				return true;
			}
			else
			{
				// Load complete
				return false;
			}
		}
		
		// Load the logo
		protected function LoadLogo():void
		{
			// Get the logo container
			var pContainer:Form = Form(UI.findViewById("login_container"));
			
			// Load the logo
			var pAttributes:Attributes = new Attributes(0, 0, width, height);
			m_pLogo = new Logo(pContainer, LOGO, pAttributes);
			
			// Append the logo to the XML and refresh
			pContainer.xml.appendChild(LOGO);
			pContainer.AppendChild(m_pLogo);
			layout(attributes);
		}

		// Load the login
		protected function LoadLogin():void
		{
			// Get the logo container
			var pContainer:Form = Form(UI.findViewById("login_container"));
			
			// Load the login
			var pAttributes:Attributes = new Attributes(0, 0, width, height);
			m_pLogin = new Screen(pContainer, m_pElixys, LOGIN, pAttributes);
			m_pLogin.visible = false;
			
			// Append the logo to the XML and refresh
			pContainer.xml.appendChild(LOGIN);
			pContainer.AppendChild(m_pLogin);
			layout(attributes);
			
			// Get references to the view components
			m_pServer = Input(UI.findViewById("server"));
			m_pUsername = Input(UI.findViewById("username"));
			m_pPassword = Input(UI.findViewById("password"));
			m_pLoginButton = Button(UI.findViewById("login"));
			m_pErrorText = UILabel(UI.findViewById("login_error_text"));
			
			// Add event listeners
			m_pServer.inputField.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_ACTIVATE, OnKeyboardChange);
			m_pServer.inputField.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_DEACTIVATE, OnKeyboardChange);
			m_pServer.inputField.addEventListener(KeyboardEvent.KEY_DOWN, OnServerKeyDown);
			m_pServer.addEventListener(TextEvent.TEXT_INPUT, OnInputChanged);
			m_pUsername.inputField.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_ACTIVATE, OnKeyboardChange);
			m_pUsername.inputField.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_DEACTIVATE, OnKeyboardChange);
			m_pUsername.inputField.addEventListener(KeyboardEvent.KEY_DOWN, OnUsernameKeyDown);
			m_pUsername.addEventListener(TextEvent.TEXT_INPUT, OnInputChanged);
			m_pPassword.inputField.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_ACTIVATE, OnKeyboardChange);
			m_pPassword.inputField.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_DEACTIVATE, OnKeyboardChange);
			m_pPassword.inputField.addEventListener(KeyboardEvent.KEY_DOWN, OnPasswordKeyDown);
			m_pPassword.addEventListener(TextEvent.TEXT_INPUT, OnInputChanged);
			m_pLoginButton.addEventListener(ButtonEvent.CLICK, OnLoginButton);
			
			// Initialize the text fields
			m_pLocalData = SharedObject.getLocal("Elixys");
			if (m_pLocalData.data.server != null)
			{
				m_pServer.text = m_pLocalData.data.server;
			}
			if (m_pLocalData.data.username != null)
			{
				m_pUsername.text = m_pLocalData.data.username;
			}
			
			// Determine the area of the stage that should remain visible when the soft keyboard is raised
			m_nInputAreaOfInterestTop = m_pServer.getBounds(stage).top; 
			m_nInputAreaOfInterestBottom = m_pLoginButton.getBounds(stage).bottom; 
		}
		
		/***
		 * Member functions
		 **/

		// Called when this view is first displayed
		public function InitialDisplay():void
		{
			// Fade in the login fields
			m_pLogin.addEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnFadeTransitionComplete);
			m_pLogin.Fade(0, 1, 350);
		}
		
		// Called to set the error text
		public function SetError(sError:String):void
		{
			m_pErrorText.text = sError;
		}
		
		// Called when the soft keyboard actives or deactivates
		protected function OnKeyboardChange(event:SoftKeyboardEvent):void
		{
			// Pan the application
			m_pElixys.PanApplication(m_nInputAreaOfInterestTop, m_nInputAreaOfInterestBottom);
		}
		
		// Called when the initial fade in transition completes
		protected function OnFadeTransitionComplete(event:TransitionCompleteEvent):void
		{
			// Remove the event listener
			m_pLogin.removeEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnFadeTransitionComplete);
			
			// Give the input focus to the input field that does not have text
			if (m_pServer.text == "")
			{
				m_pServer.inputField.assignFocus();
			}
			else if (m_pUsername.text == "")
			{
				m_pUsername.inputField.assignFocus();
			}
			else
			{
				m_pPassword.inputField.assignFocus();
			}
		}

		// Called when the server field receives a key down event
		protected function OnServerKeyDown(event:KeyboardEvent):void
		{
			// Either tab or return moves the focus to the username field
			if ((event.keyCode == CHAR_TAB) || (event.keyCode == CHAR_RETURN))
			{
				event.preventDefault();
				m_pUsername.inputField.assignFocus();
			}
		}

		// Called when the username field receives a key down event
		protected function OnUsernameKeyDown(event:KeyboardEvent):void
		{
			// Either tab or return moves the focus to the password field
			if ((event.keyCode == CHAR_TAB) || (event.keyCode == CHAR_RETURN))
			{
				event.preventDefault();
				m_pPassword.inputField.assignFocus();
			}
		}
		
		// Called when the password field receives a key down event
		protected function OnPasswordKeyDown(event:KeyboardEvent):void
		{
			if ((event.keyCode == CHAR_TAB) || (event.keyCode == CHAR_RETURN))
			{
				// Return logs in if all fields contain text, otherwise move the focus back to the server field
				if ((event.keyCode == CHAR_RETURN) && (m_pServer.text != "") && (m_pUsername.text != "") && (m_pPassword.text != ""))
				{
					LogIn();
				}
				else
				{
					event.preventDefault();
					m_pServer.inputField.assignFocus();
				}
			}
		}

		// Called when the text in any of the input fields is changed
		protected function OnInputChanged(event:TextEvent):void
		{
			// Update the login button state
			m_pLoginButton.enabled = ((m_pServer.text != "") && (m_pUsername.text != "") && (m_pPassword.text != ""));
		}

		// Called when the user clicks the login button
		protected function OnLoginButton(event:ButtonEvent):void
		{
			LogIn();
		}
		
		// Logs in to the server
		protected function LogIn():void
		{
			// Save the server and username to local storage
			m_pLocalData.data.server = m_pServer.text;
			m_pLocalData.data.username = m_pUsername.text;
			m_pLocalData.flush();
		
			// Create a connection to the server
			m_pElixys.ConnectToServer(m_pServer.text, m_pUsername.text, m_pPassword.text);
		}

		/***
		 * Member variables
		 **/
		
		// Login screen XML
		protected static const LOGIN_SCREEN:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignV="fill" alignH="fill">
				<rows gapV="0" border="false" heights="18%,64%" background={Styling.APPLICATION_BACKGROUND}>
					<frame />
					<columns id="login_container" gapH="0" widths="34%,66%" />
				</rows>
			</frame>;

		// Logo XML
		protected static const LOGO:XML = 
			<logo id="Logo" />;
		
		// Login component XML
		protected static const LOGIN:XML =
			<rows gapV="5" heights="35%,7%,9%,7%,9%,5%,9%,19%">
				<frame />
				<label useEmbedded="true" alignH="left" alignV="bottom">
					<font face="GothamBold" color={Styling.TEXT_LIGHTERGRAY} size="12">
						SERVER
					</font>
				</label>
				<input id="server" alignH="fill" alignV="fill" color={Styling.TEXT_DARKERGRAY} size="32" 
					skin={getQualifiedClassName(login_serverFieldBackground_mc)} returnKeyLabel={Constants.RETURNKEYLABEL_NEXT} />
				<columns gapH="25" widths="50%,50%">
					<label useEmbedded="true" alignH="left" alignV="bottom">
						<font face="GothamBold" color={Styling.TEXT_LIGHTERGRAY} size="12">
							USERNAME
						</font>
					</label>
					<label useEmbedded="true" alignH="left" alignV="bottom">
						<font face="GothamBold" color={Styling.TEXT_LIGHTERGRAY} size="12">
							PASSWORD
						</font>
					</label>
				</columns>
				<columns gapH="25" widths="50%,50%">
					<input id="username" alignH="fill" alignV="fill" color={Styling.TEXT_DARKERGRAY} size="32" 
						skin={getQualifiedClassName(login_loginFieldBackground_mc)} returnKeyLabel={Constants.RETURNKEYLABEL_NEXT} />
					<input id="password" alignH="fill" alignV="fill" color={Styling.TEXT_DARKERGRAY} size="32" 
						skin={getQualifiedClassName(login_loginFieldBackground_mc)} returnKeyLabel={Constants.RETURNKEYLABEL_GO} 
						displayAsPassword="true" />
				</columns>
				<frame />
				<columns gapH="35" widths="49%,51%">
					<frame alignH="fill" alignV="fill">
						<button id="login" alignH="fill" alignV="fill" enabled="false" useEmbedded="true"
								enabledTextColor={Styling.TEXT_DARKERGRAY} disabledTextColor={Styling.TEXT_LIGHTGRAY}
								skinup={getQualifiedClassName(login_signIn_up)}
								skindown={getQualifiedClassName(login_signIn_down)}
								skindisabled={getQualifiedClassName(login_signIn_disabled)}>
							<font face="GothamMedium" size="14">
								Sign in
							</font>
						</button>
					</frame>
					<label id="login_error_text" useEmbedded="true" alignH="fill" alignV="top">
						<font face="GothamMedium" color={Styling.TEXT_RED} size="14" />
					</label>
				</columns>
			</rows>;

		// Screen components
		protected var m_pLogo:Logo;
		protected var m_pLogin:Form;
		protected var m_pServer:UIInput;
		protected var m_pUsername:UIInput;
		protected var m_pPassword:UIInput;
		protected var m_pLoginButton:Button;
		protected var m_pErrorText:UILabel;

		// Number of steps required to load this object
		public static var LOAD_STEPS:uint = 2;
		
		// The current step
		protected var m_nChildrenLoaded:uint = 0;

		// Character codes
		public static const CHAR_RETURN:uint = 13;
		public static const CHAR_TAB:uint = 9;
		
		// Input area of interest
		protected var m_nInputAreaOfInterestTop:uint;
		protected var m_nInputAreaOfInterestBottom:uint;

		// Shared object for persistent local storage
		protected var m_pLocalData:SharedObject;
	}
}

