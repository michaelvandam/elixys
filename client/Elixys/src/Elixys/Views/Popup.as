package Elixys.Views
{
	import Elixys.Assets.Constants;
	import Elixys.Assets.Styling;
	import Elixys.Components.*;
	import Elixys.Events.ButtonEvent;
	import Elixys.Extended.Form;
	import Elixys.Extended.Input;
	import Elixys.JSON.Post.PostPrompt;
	import Elixys.JSON.Post.PostSelect;
	import Elixys.JSON.State.*;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.events.KeyboardEvent;
	import flash.events.MouseEvent;
	import flash.events.SoftKeyboardEvent;
	import flash.events.TextEvent;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.*;
	
	// This popup view is an extension of the Screen class
	public class Popup extends Screen
	{
		/***
		 * Construction
		 **/
		
		public function Popup(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, POPUP, attributes, row, inGroup);
			
			// Get references to our view components
			m_pBackground = findViewById("popup_background") as Form;
			m_pContents = findViewById("popup_contents") as Form;
			m_pTitle = findViewById("popup_title") as UILabel;
			m_pText1 = findViewById("popup_text1") as UILabel;
			m_pInput1 = findViewById("popup_input1") as Input;
			m_pText2 = findViewById("popup_text2") as UILabel;
			m_pInput2 = findViewById("popup_input2") as Input;
			m_pButton1Container = findViewById("popup_button1_container") as Form;
			m_pButton2Container = findViewById("popup_button2_container") as Form;
			m_pButton1 = findViewById("popup_button1") as Elixys.Components.Button;
			m_pButton2 = findViewById("popup_button2") as Elixys.Components.Button;
			
			// Set the background transparency and center the popup
			m_pBackground.alpha = 0.8;
			CenterPopup();
			
			// Add event handlers
			m_pInput1.inputField.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_ACTIVATE, OnKeyboardChange);
			m_pInput1.inputField.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_DEACTIVATE, OnKeyboardChange);
			m_pInput1.inputField.addEventListener(KeyboardEvent.KEY_DOWN, OnInput1KeyDown);
			m_pInput1.addEventListener(TextEvent.TEXT_INPUT, OnInputChanged);
			m_pInput2.inputField.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_ACTIVATE, OnKeyboardChange);
			m_pInput2.inputField.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_DEACTIVATE, OnKeyboardChange);
			m_pInput2.inputField.addEventListener(KeyboardEvent.KEY_DOWN, OnInput2KeyDown);
			m_pInput2.addEventListener(TextEvent.TEXT_INPUT, OnInputChanged);
			m_pButton1.addEventListener(ButtonEvent.CLICK, OnButtonClick);
			m_pButton2.addEventListener(ButtonEvent.CLICK, OnButtonClick);
		}

		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public override function LoadNext():Boolean
		{
			// This screen is simple, load everything at once
			return false;
		}

		/***
		 * Member functions
		 **/
		
		// Updates the state
		public override function UpdateState(pState:State):void
		{
			// Check if the prompt state has changed
			if ((m_pPromptState != null) && PromptState.ComparePromptStates(pState.ClientState.PromptState, m_pPromptState))
			{
				return;
			}
			
			// Remember the new prompt state
			m_pPromptState = pState.ClientState.PromptState;
			
			// Update the text
			m_pTitle.text = m_pPromptState.Title;
			if (m_pPromptState.Text1 != "")
			{
				m_pText1.text = m_pPromptState.Text1;
				m_pText1.visible = true;
			}
			else
			{
				m_pText1.visible = false;
			}
			if (m_pPromptState.Edit1)
			{
				m_pInput1.text = m_pPromptState.Edit1Default;
				m_pInput1.visible = true;
			}
			else
			{
				m_pInput1.visible = false;
			}
			if (m_pPromptState.Text2 != "")
			{
				m_pText2.text = m_pPromptState.Text2;
				m_pText2.visible = true;
			}
			else
			{
				m_pText2.visible = false;
			}
			if (m_pPromptState.Edit2)
			{
				m_pInput2.text = m_pPromptState.Edit2Default;
				m_pInput2.visible = true;
			}
			else
			{
				m_pInput2.visible = false;
			}
			var pButton:Elixys.JSON.State.Button;
			if (m_pPromptState.Buttons.length > 0)
			{
				pButton = m_pPromptState.Buttons[0] as Elixys.JSON.State.Button;
				m_pButton1.text = pButton.Text;
				m_pButton1.visible = true;
			}
			else
			{
				m_pButton1.visible = false;
			}
			if (m_pPromptState.Buttons.length > 1)
			{
				pButton = m_pPromptState.Buttons[1] as Elixys.JSON.State.Button;
				m_pButton2.text = pButton.Text;
				m_pButton2.visible = true;
			}
			else
			{
				m_pButton2.visible = false;
			}
			layout(attributes);

			// Render
			Render();
			
			// Determine the area of the stage that should remain visible when the soft keyboard is raised
			m_nInputAreaOfInterestTop = m_pTitle.getBounds(stage).top; 
			m_nInputAreaOfInterestBottom = m_pButton1.getBounds(stage).bottom;
			
			// Set the keyboard focus
			if (m_pInput1.visible)
			{
				m_pInput1.inputField.assignFocus();
			}
		}
		
		// Render the popup
		protected function Render():void
		{
			// Set the popup width
			m_pContents.attributes.width = m_pBackground.attributes.width * POPUP_PERCENT_WIDTH / 100;
			
			// Adjust the title position
			var nOffset:int = POPUP_BORDER;
			m_pTitle.x = (m_pContents.attributes.width - m_pTitle.textWidth) / 2;
			m_pTitle.y = nOffset;
			nOffset += m_pTitle.textHeight + POPUP_GAP_BIG;
			
			// Adjust the first text and input
			if (m_pText1.visible)
			{
				m_pText1.width = m_pContents.attributes.width - (POPUP_BORDER * 2);
				if (m_pText1.textWidth < m_pText1.width)
				{
					m_pText1.width = m_pText1.textWidth + 8;
				}
				m_pText1.x = ((m_pContents.attributes.width - m_pText1.width - (POPUP_BORDER * 2)) / 2) + POPUP_BORDER;
				m_pText1.y = nOffset;
				nOffset += m_pText1.textHeight;
			}
			if (m_pText1.visible && m_pInput1.visible)
			{
				nOffset += POPUP_GAP_SMALL;
			}
			if (m_pInput1.visible)
			{
				m_pInput1.parent.x = POPUP_BORDER;
				m_pInput1.parent.y = nOffset;
				m_pInput1.parent.width = m_pContents.attributes.width - (POPUP_BORDER * 2);
				m_pInput1.fixwidth = m_pInput1.parent.width;
				nOffset += m_pInput1.height;
			}
			nOffset += POPUP_GAP_BIG;
			
			// Adjust the second text and edit
			if (m_pText2.visible)
			{
				m_pText2.width = m_pContents.attributes.width - (POPUP_BORDER * 2);
				if (m_pText2.textWidth < m_pText2.width)
				{
					m_pText2.width = m_pText2.textWidth + 8;
				}
				m_pText2.x = ((m_pContents.attributes.width - m_pText2.width - (POPUP_BORDER * 2)) / 2) + POPUP_BORDER;
				m_pText2.y = nOffset;
				nOffset += m_pText2.textHeight;
			}
			if (m_pText2.visible && m_pInput2.visible)
			{
				nOffset += POPUP_GAP_SMALL;
			}
			if (m_pInput2.visible)
			{
				m_pInput2.parent.x = POPUP_BORDER;
				m_pInput2.parent.y = nOffset;
				m_pInput2.parent.width = m_pContents.attributes.width - (POPUP_BORDER * 2);
				m_pInput2.fixwidth = m_pInput2.parent.width;
				nOffset += m_pInput2.height;
			}
			
			// Adjust the buttons
			nOffset += POPUP_GAP_BIG;
			if (!m_pButton2.visible)
			{
				// Center the single button
				m_pButton1Container.x = m_pContents.attributes.width - m_pButton1.width;
				m_pButton1Container.y = nOffset;
				nOffset += m_pButton1.height + POPUP_BORDER;
			}
			else
			{
				// Center both buttons
				m_pButton1Container.x = (m_pContents.attributes.width / 2) - POPUP_GAP_BIG - m_pButton1.width;
				m_pButton1Container.y = nOffset;
				m_pButton2Container.x = (m_pContents.attributes.width / 2) + POPUP_GAP_BIG;
				m_pButton2Container.y = nOffset;
				nOffset += m_pButton1.height + POPUP_BORDER;
			}
			
			// Set the total height
			m_pContents.attributes.height = nOffset;
			
			// Paint the background
			m_pContents.graphics.clear();
			m_pContents.graphics.beginFill(Styling.AS3Color(Styling.POPUP_BACKGROUND));
			m_pContents.graphics.drawRoundRect(0, 0, m_pContents.attributes.width, m_pContents.attributes.height,
				POPUP_CURVE, POPUP_CURVE);
			m_pContents.graphics.endFill();

			// Make sure the popup is centered
			CenterPopup();
		}
		
		// Centers the popup
		protected function CenterPopup():void
		{
			m_pContents.x = (m_pBackground.attributes.width - m_pContents.attributes.width) / 2;
			m_pContents.y = (m_pBackground.attributes.height - m_pContents.attributes.height) / 2;
		}
		
		// Called when a button on the navigation bar is clicked
		protected function OnButtonClick(event:ButtonEvent):void
		{
			// Send a button click to the server
			var pPostPrompt:PostPrompt = new PostPrompt();
			if (event.button == "popup_button1")
			{
				pPostPrompt.TargetID = (m_pPromptState.Buttons[0] as Elixys.JSON.State.Button).ID;
			}
			else
			{
				pPostPrompt.TargetID = (m_pPromptState.Buttons[1] as Elixys.JSON.State.Button).ID;
			}
			if (m_pPromptState.Edit1)
			{
				pPostPrompt.Edit1 = m_pInput1.text;
			}
			if (m_pPromptState.Edit2)
			{
				pPostPrompt.Edit2 = m_pInput2.text;
			}
			DoPost(pPostPrompt, "PROMPT");
		}

		// Called when the soft keyboard actives or deactivates
		protected function OnKeyboardChange(event:SoftKeyboardEvent):void
		{
			// Pan the application
			m_pElixys.PanApplication(m_nInputAreaOfInterestTop, m_nInputAreaOfInterestBottom);
		}

		// Called when the first input field receives a key down event
		protected function OnInput1KeyDown(event:KeyboardEvent):void
		{
			/*
			// Either tab or return moves the focus to the username field
			if ((event.keyCode == CHAR_TAB) || (event.keyCode == CHAR_RETURN))
			{
				event.preventDefault();
				m_pUsername.inputField.assignFocus();
			}
			*/
		}

		// Called when the second input field receives a key down event
		protected function OnInput2KeyDown(event:KeyboardEvent):void
		{
			/*
			// Either tab or return moves the focus to the password field
			if ((event.keyCode == CHAR_TAB) || (event.keyCode == CHAR_RETURN))
			{
				event.preventDefault();
				m_pPassword.inputField.assignFocus();
			}
			*/
		}

		// Called when the text in any of the input fields is changed
		protected function OnInputChanged(event:TextEvent):void
		{
			// Update the login button state
			//m_pLoginButton.enabled = ((m_pServer.text != "") && (m_pUsername.text != "") && (m_pPassword.text != ""));
		}

		/***
		 * Member variables
		 **/

		// Popup XML
		protected static const POPUP:XML = 
			<frame alignH="fill" alignV="fill">
				<frame id="popup_background" background={Styling.TEXT_GRAY1} alignH="fill" alignV="fill" />
				<frame id="popup_contents">
					<label id="popup_title" useEmbedded="true">
						<font face="GothamMedium" size="20" />
					</label>
					<label id="popup_text1" useEmbedded="true" width="350" includeInLayout="false">
						<font face="GothamMedium" size="18" />
					</label>
					<frame width={INPUT_WIDTH} height={INPUT_HEIGHT}>
						<input id="popup_input1" color={Styling.TEXT_GRAY1} width={INPUT_WIDTH} height={INPUT_HEIGHT}
							size="24" skin={getQualifiedClassName(login_serverFieldBackground_mc)}
							returnKeyLabel={Constants.RETURNKEYLABEL_NEXT} />
					</frame>
					<label id="popup_text2" useEmbedded="true" width="350">
						<font face="GothamMedium" size="18" />
					</label>
					<frame width={INPUT_WIDTH} height={INPUT_HEIGHT}>
						<input id="popup_input2" color={Styling.TEXT_GRAY1} width={INPUT_WIDTH} height={INPUT_HEIGHT}
							size="24" skin={getQualifiedClassName(login_serverFieldBackground_mc)}
							returnKeyLabel={Constants.RETURNKEYLABEL_GO} />
					</frame>
					<frame id="popup_button1_container" width={POPUP_BUTTON_WIDTH} height={POPUP_BUTTON_HEIGHT}>
						<button id="popup_button1" enabled="true" useEmbedded="true" enabledTextColor={Styling.TEXT_GRAY1}
								disabledTextColor={Styling.TEXT_GRAY6} pressedTextColor={Styling.TEXT_WHITE}
								backgroundskinup={getQualifiedClassName(popupBtn_up)}
								backgroundskindown={getQualifiedClassName(popupBtn_down)}>
							<font face="GothamMedium" size="14" />
						</button>
					</frame>
					<frame id="popup_button2_container" width={POPUP_BUTTON_WIDTH} height={POPUP_BUTTON_HEIGHT}>
						<button id="popup_button2" enabled="true" useEmbedded="true" enabledTextColor={Styling.TEXT_GRAY1}
								disabledTextColor={Styling.TEXT_GRAY6} pressedTextColor={Styling.TEXT_WHITE}
								backgroundskinup={getQualifiedClassName(popupBtn_up)}
								backgroundskindown={getQualifiedClassName(popupBtn_down)}>
							<font face="GothamMedium" size="14" />
						</button>
					</frame>
				</frame>
			</frame>;

		// Number of steps required to load this object
		public static var LOAD_STEPS:uint = 0;
		
		// Currently displayed prompt state
		protected var m_pPromptState:PromptState;

		// Screen components
		protected var m_pBackground:Form;
		protected var m_pContents:Form;
		protected var m_pTitle:UILabel;
		protected var m_pText1:UILabel;
		protected var m_pInput1:Input;
		protected var m_pText2:UILabel;
		protected var m_pInput2:Input;
		protected var m_pButton1Container:Form;
		protected var m_pButton2Container:Form;
		protected var m_pButton1:Elixys.Components.Button;
		protected var m_pButton2:Elixys.Components.Button;
		
		// Input area of interest
		protected var m_nInputAreaOfInterestTop:uint;
		protected var m_nInputAreaOfInterestBottom:uint;

		// Constants
		public static const POPUP_PERCENT_WIDTH:int = 50;
		public static const POPUP_BORDER:int = 38;
		public static const POPUP_GAP_BIG:int = 15;
		public static const POPUP_GAP_SMALL:int = 5;
		public static const POPUP_CURVE:uint = 15;
		public static const POPUP_BUTTON_WIDTH:int = 110;
		public static const POPUP_BUTTON_HEIGHT:int = 35;
		protected static const INPUT_WIDTH:int = 200;
		protected static const INPUT_HEIGHT:int = 33;
	}
}
