package Elixys.Views
{
	import Elixys.Assets.Constants;
	import Elixys.Assets.Styling;
	import Elixys.Events.*;
	import Elixys.Extended.*;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.InteractiveObject;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.KeyboardEvent;
	import flash.events.SoftKeyboardEvent;
	import flash.events.TextEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.net.SharedObject;
	import flash.ui.Keyboard;
	import flash.utils.*;

	// This loading view is an extension of our extended Form class
	public class Login extends Form
	{
		/***
		 * Construction
		 **/
		
		public function Login(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			super(screen, LOGIN, attributes, row, inGroup);
		}

		// Called when this view is first displayed
		public function InitialDisplay():void
		{
			// Get references to the view components
			m_pLoginFields = Form(UI.findViewById("loginfields"));
			m_pServer = Input(UI.findViewById("server"));
			m_pUsername = Input(UI.findViewById("username"));
			m_pPassword = Input(UI.findViewById("password"));
			m_pLogin = Button(UI.findViewById("login"));

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

			// Fade in the login fields
			m_pLoginFields.addEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnFadeTransitionComplete);
			m_pLoginFields.Fade(0, 1, 350);
			
			// Determine the area of the stage that should remain visible when the soft keyboard is raised
			m_nInputAreaOfInterestTop = m_pServer.getBounds(stage).top; 
			m_nInputAreaOfInterestBottom = m_pLogin.getBounds(stage).bottom; 
		}
		
		// Called when the soft keyboard actives or deactivates
		protected function OnKeyboardChange(event:SoftKeyboardEvent):void
		{
			// Pan the application
			GetMainApplication().PanApplication(m_nInputAreaOfInterestTop, m_nInputAreaOfInterestBottom);
		}
		
		/***
		 * Member functions
		 **/

		// Called when the initial fade in transition completes
		protected function OnFadeTransitionComplete(event:TransitionCompleteEvent):void
		{
			// Remove the event listener
			m_pLoginFields.removeEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnFadeTransitionComplete);
			
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
					// Save the server and username to local storage
					m_pLocalData.data.server = m_pServer.text;
					m_pLocalData.data.username = m_pUsername.text;
					m_pLocalData.flush();
					
					// Create a connection to the server
					GetMainApplication().ConnectToServer(m_pServer.text, m_pUsername.text, m_pPassword.text);
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
			m_pLogin.enabled = ((m_pServer.text != "") && (m_pUsername.text != "") && (m_pPassword.text != ""));
		}
		
		/***
		 * Member variables
		 **/
		
		// Login view XML
		protected static const LOGIN:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND}>
				<rows gapV="0" border="false" heights="18%,64%" background={Styling.APPLICATION_BACKGROUND}>
					<frame />
					<columns gapH="0" widths="50%,40%">
						<logo id="Logo" />
						<rows id="loginfields" visible="false" gapV="5" heights="32%,7%,7%,7%,7%,3%,8%,29%">
							<frame />
							<label useEmbedded="true" alignH="left" alignV="bottom">
								<font face="GothamMedium" color={Styling.TEXT_GRAY} size="14">
									SERVER
								</font>
							</label>
							<input id="server" alignH="fill" color={Styling.TEXT_GRAY} size="20" 
								returnKeyLabel={Constants.RETURNKEYLABEL_NEXT} />
							<columns gapH="25" widths="50%,50%">
								<label useEmbedded="true" alignH="left" alignV="bottom">
									<font face="GothamMedium" color={Styling.TEXT_GRAY} size="14">
										USERNAME
									</font>
								</label>
								<label useEmbedded="true" alignH="left" alignV="bottom">
									<font face="GothamMedium" color={Styling.TEXT_GRAY} size="14">
										PASSWORD
									</font>
								</label>
							</columns>
							<columns gapH="25" widths="50%,50%">
								<input id="username" alignH="fill" color={Styling.TEXT_GRAY} size="20" 
									returnKeyLabel={Constants.RETURNKEYLABEL_NEXT} />
								<input id="password" alignH="fill" color={Styling.TEXT_GRAY} size="20" 
									returnKeyLabel={Constants.RETURNKEYLABEL_GO} displayAsPassword="true" />
							</columns>
							<frame />
							<columns widths="50%,50%,20">
								<frame />
								<button id="login" alignH="fill" enabled="false" useEmbedded="true"
									enabledTextColor={Styling.TEXT_GRAY} disabledTextColor={Styling.TEXT_LIGHTGRAY}
									skinup={getQualifiedClassName(signIn_btn_up)} skindown={getQualifiedClassName(signIn_btn_down)}
									skindisabled={getQualifiedClassName(signIn_btn_disabled)}>
									<font face="GothamMedium" size="14">
										Sign in
									</font>
								</button>
							</columns>
						</rows>
					</columns>
				</rows>
			</frame>;
		
		// References to components
		protected var m_pLoginFields:Form;
		protected var m_pServer:UIInput;
		protected var m_pUsername:UIInput;
		protected var m_pPassword:UIInput;
		protected var m_pLogin:Button;

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

