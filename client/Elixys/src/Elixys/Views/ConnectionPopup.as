package Elixys.Views
{
	import Elixys.Assets.Styling;
	import Elixys.Components.Screen;
	import Elixys.Events.ButtonEvent;
	import Elixys.Extended.Form;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.utils.*;
	
	// This connection popup view is an extension of the Screen class
	public class ConnectionPopup extends Screen
	{
		/***
		 * Construction
		 **/
		
		public function ConnectionPopup(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, CONNECTION_POPUP, attributes, row, inGroup);
			
			// Get references to our view components
			m_pBackground = findViewById("connection_popup_background") as Form;
			m_pContents = findViewById("connection_popup_contents") as Form;
			m_pTitle = findViewById("connection_popup_title") as UILabel;
			m_pText = findViewById("connection_popup_text") as UILabel;
			m_pButtonContainer = findViewById("connection_popup_button_container") as Form;
			m_pButton = findViewById("connection_popup_button") as Elixys.Components.Button;
			
			// Set the background transparency
			m_pBackground.alpha = 0.8;
			
			// Add event handlers
			m_pButton.addEventListener(ButtonEvent.CLICK, OnButtonClick);
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

		// Set the popup text
		public function SetText(sTitle:String, sText:String, sButtonText:String):void
		{
			// Set the title, text and button
			m_pTitle.text = sTitle;
			m_pText.text = sText;
			m_pButton.text = m_sButtonText = sButtonText;
			
			// Update the layout
			layout(attributes);

			// Set the popup width
			m_pContents.attributes.width = m_pBackground.attributes.width * Popup.POPUP_PERCENT_WIDTH / 100;
			
			// Adjust the title position
			var nOffset:int = Popup.POPUP_BORDER;
			m_pTitle.x = (m_pContents.attributes.width - m_pTitle.textWidth) / 2;
			m_pTitle.y = nOffset;
			nOffset += m_pTitle.textHeight + (Popup.POPUP_GAP_BIG * 2);
			
			// Adjust the text position
			m_pText.width = m_pContents.attributes.width - (Popup.POPUP_BORDER * 2);
			if (m_pText.textWidth < m_pText.width)
			{
				m_pText.width = m_pText.textWidth + 8;
			}
			m_pText.x = ((m_pContents.attributes.width - m_pText.width - (Popup.POPUP_BORDER * 2)) / 2) +
				Popup.POPUP_BORDER;
			m_pText.y = nOffset;
			nOffset += m_pText.textHeight;
			nOffset += Popup.POPUP_GAP_BIG * 2;
			
			// Adjust the button
			m_pButtonContainer.x = (m_pContents.attributes.width - m_pButton.width) / 2;
			m_pButtonContainer.y = nOffset;
			nOffset += m_pButton.height + Popup.POPUP_BORDER;
			
			// Set the total height
			m_pContents.attributes.height = nOffset;
			
			// Paint the background
			m_pContents.graphics.clear();
			m_pContents.graphics.beginFill(Styling.AS3Color(Styling.POPUP_BACKGROUND));
			m_pContents.graphics.drawRoundRect(0, 0, m_pContents.attributes.width, m_pContents.attributes.height,
				Popup.POPUP_CURVE, Popup.POPUP_CURVE);
			m_pContents.graphics.endFill();

			// Make sure the popup is centered
			m_pContents.x = (m_pBackground.attributes.width - m_pContents.attributes.width) / 2;
			m_pContents.y = (m_pBackground.attributes.height - m_pContents.attributes.height) / 2;
		}
		
		// Called when the cancel button is clicked
		protected function OnButtonClick(event:ButtonEvent):void
		{
			dispatchEvent(new ButtonEvent(m_sButtonText));
		}

		/***
		 * Member variables
		 **/

		// Popup XML
		protected static const CONNECTION_POPUP:XML = 
			<frame alignH="fill" alignV="fill">
				<frame id="connection_popup_background" background={Styling.TEXT_GRAY1} alignH="fill" alignV="fill" />
				<frame id="connection_popup_contents">
					<label id="connection_popup_title" useEmbedded="true">
						<font face="GothamMedium" size="20" />
					</label>
					<label id="connection_popup_text" useEmbedded="true" width="350">
						<font face="GothamMedium" size="18" />
					</label>
					<frame id="connection_popup_button_container" width={Popup.POPUP_BUTTON_WIDTH} height={Popup.POPUP_BUTTON_HEIGHT}>
						<button id="connection_popup_button" enabled="true" useEmbedded="true" enabledTextColor={Styling.TEXT_GRAY1}
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
		
		// View components
		protected var m_pBackground:Form;
		protected var m_pContents:Form;
		protected var m_pTitle:UILabel;
		protected var m_pText:UILabel;
		protected var m_pButtonContainer:Form;
		protected var m_pButton:Elixys.Components.Button;
		protected var m_sButtonText:String;
		
		// Listener
		public var listener:Function;
	}
}
