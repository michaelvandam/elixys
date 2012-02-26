package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Extended.*;
	import Elixys.JSON.State.Button;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.text.TextFieldAutoSize;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.*;

	// This navigation bar component is an extension of the Form class
	public class NavigationBar extends Form
	{
		/***
		 * Construction
		 **/
		
		public function NavigationBar(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false,
			inGroup:Boolean = false)
		{
			// Process the navigation bar options
			var pButtonText:Array = new Array();
			var pForegroundSkinUpName:Array = new Array();
			var pForegroundSkinDownName:Array = new Array();
			var pForegroundSkinDisabledName:Array = new Array();
			var pBackgroundSkinUpName:Array = new Array();
			var pBackgroundSkinDownName:Array = new Array();
			var pBackgroundSkinDisabledName:Array = new Array();
			while (xml.navigationbaroption.length() > 0)
			{
				// Extract the details
				var pButtonXML:XML = xml.navigationbaroption[0];
				pButtonText.push(pButtonXML.toString());
				m_pButtonNames.push(pButtonXML.@name[0]);
				m_pForegroundSkinHeights.push(pButtonXML.@foregroundskinheightpercent[0]);
				m_pForegroundSkinWidths.push(pButtonXML.@foregroundskinwidthpercent[0]);
				pForegroundSkinUpName.push(pButtonXML.@foregroundskinup[0]);
				pForegroundSkinDownName.push(pButtonXML.@foregroundskindown[0]);
				pForegroundSkinDisabledName.push(pButtonXML.@foregroundskindisabled[0]);
				pBackgroundSkinUpName.push(pButtonXML.@backgroundskinup[0]);
				pBackgroundSkinDownName.push(pButtonXML.@backgroundskindown[0]);
				pBackgroundSkinDisabledName.push(pButtonXML.@backgroundskindisabled[0]);

				// Buttons are disabled by default
				m_pButtonEnabled.push(false);

				// Remove the node from the XML
				delete xml.children()[pButtonXML.childIndex()];
			}
			
			// Call the base constructor
			super(screen, xml, attributes, row, inGroup);
			
			// Determine our current width and height
			var nWidth:int = FindWidth(screen);
			var nHeight:int = FindHeight(screen);

			// Get the text colors
			if (xml.@enabledTextColor.length() > 0)
			{
				m_nEnabledText = Styling.AS3Color(xml.@enabledTextColor[0]);
			}
			if (xml.@disabledTextColor.length() > 0)
			{
				m_nDisabledText = Styling.AS3Color(xml.@disabledTextColor[0]);
			}

			// Set the background skin
			if (xml.@skin.length() > 0)
			{
				m_pMainSkin = AddSkin(xml.@skin[0]);
				m_pMainSkin.width = nWidth + MAIN_SKIN_PADDING;
				m_pMainSkin.height = nHeight;
			}

			// Create the visual components
			var nForegroundSkinHeight:int = 0;
			for (var nButton:int = 0; nButton < pButtonText.length; ++nButton)
			{
				// Create the label
				m_pButtonLabels.push(AddLabel(pButtonText[nButton]));

				// Create the button background skins
				if (pBackgroundSkinUpName[nButton] != null)
				{
					m_pBackgroundSkinUp.push(AddSkin(pBackgroundSkinUpName[nButton]));
					SetBackgroundSkinPosition(nButton, pButtonText.length, nWidth, nHeight, m_pBackgroundSkinUp[nButton]);
				}
				if (pBackgroundSkinDownName[nButton] != null)
				{
					m_pBackgroundSkinDown.push(AddSkin(pBackgroundSkinDownName[nButton]));
					SetBackgroundSkinPosition(nButton, pButtonText.length, nWidth, nHeight, m_pBackgroundSkinDown[nButton]);
				}
				if (pBackgroundSkinDisabledName[nButton] != null)
				{
					m_pBackgroundSkinDisabled.push(AddSkin(pBackgroundSkinDisabledName[nButton]));
					SetBackgroundSkinPosition(nButton, pButtonText.length, nWidth, nHeight, m_pBackgroundSkinDisabled[nButton]);
				}
				
				// Create the foreground skins
				if ((m_pForegroundSkinWidths[nButton] != null) || (m_pForegroundSkinHeights[nButton] != null))
				{
					if (pForegroundSkinUpName[nButton] != null)
					{
						m_pForegroundSkinUp.push(AddSkin(pForegroundSkinUpName[nButton]));
						nForegroundSkinHeight = SetForegroundSkinPosition(nButton, pButtonText.length, nWidth, nHeight,
							m_pForegroundSkinUp[nButton]);
					}
					if (pForegroundSkinDownName[nButton] != null)
					{
						m_pForegroundSkinDown.push(AddSkin(pForegroundSkinDownName[nButton]));
						nForegroundSkinHeight = SetForegroundSkinPosition(nButton, pButtonText.length, nWidth, nHeight,
							m_pForegroundSkinDown[nButton]);
					}
					if (pForegroundSkinDisabledName[nButton] != null)
					{
						m_pForegroundSkinDisabled.push(AddSkin(pForegroundSkinDisabledName[nButton]));
						nForegroundSkinHeight = SetForegroundSkinPosition(nButton, pButtonText.length, nWidth, nHeight,
							m_pForegroundSkinDisabled[nButton]);
					}
				}

				// Set the label position
				SetLabelPosition(nButton, pButtonText.length, nWidth, nHeight, nForegroundSkinHeight);
			}
			
			// Listen for resize events
			stage.addEventListener(Event.RESIZE, OnResize);
		}

		/***
		 * Member functions
		 **/

		// Add a skin
		protected function AddSkin(sClassName:String):MovieClip
		{
			var pClass:Class = getDefinitionByName(sClassName) as Class;
			var pMovieClip:MovieClip = new pClass() as MovieClip;
			addChild(pMovieClip);
			return pMovieClip;
		}
		
		// Add a label
		protected function AddLabel(sText:String):UILabel
		{
			var pXML:XML =
				<label useEmbedded="true" alignH="left" alignV="bottom">
					<font face="GothamMedium" color={Styling.TEXT_GRAY} size="14">
						{sText}
					</font>
				</label>;
			var pLabel:UILabel = CreateLabel(pXML, attributes);
			var pTextFormat:TextFormat = pLabel.getTextFormat();
			pTextFormat.align = TextFormatAlign.CENTER;
			pLabel.setTextFormat(pTextFormat);
			pLabel.textColor = m_nDisabledText;
			return pLabel;
		}

		// Sets the background skin position
		protected function SetBackgroundSkinPosition(nButton:int, nTotal:int, nWidth:int, nHeight:int, pSkin:MovieClip):void
		{
			var nTotalWidth:int = nWidth / nTotal;
			pSkin.x = nTotalWidth * nButton;
			pSkin.y = 0;
			pSkin.width = nTotalWidth;
			pSkin.height = nHeight;
		}

		// Set the foreground skin position
		protected function SetForegroundSkinPosition(nButton:int, nTotal:int, nWidth:int, nHeight:int, pSkin:MovieClip):int
		{
			// Determine the skin width and height
			var nSkinWidth:int, nSkinHeight:int;
			var nTotalWidth:int = nWidth / nTotal;
			if (m_pForegroundSkinWidths[nButton] != null)
			{
				nSkinWidth = nTotalWidth * m_pForegroundSkinWidths[nButton] / 100;
				nSkinHeight = nSkinWidth * (pSkin.height / pSkin.width);
			}
			else
			{
				nSkinHeight = nHeight * m_pForegroundSkinHeights[nButton] / 100;
				nSkinWidth = nSkinHeight * (pSkin.width / pSkin.height);
			}
			
			// Get the text height
			var nTextHeight:int = 0;
			if (m_pButtonLabels.length > nButton)
			{
				nTextHeight = UILabel(m_pButtonLabels[nButton]).textHeight;
			}
			
			// Set the skin position
			pSkin.x = (nTotalWidth * nButton) + (nTotalWidth - nSkinWidth) / 2;
			pSkin.y = (nHeight - nTextHeight - nSkinHeight - BUTTON_GAP) / 2;
			pSkin.width = nSkinWidth;
			pSkin.height = nSkinHeight;
			
			// Return the skin height
			return nSkinHeight;
		}

		// Set the label position
		protected function SetLabelPosition(nButton:int, nTotal:int, nWidth:int, nHeight:int, nForegroundSkinHeight:int):void
		{
			var pLabel:UILabel = m_pButtonLabels[nButton];
			var nTotalWidth:int = nWidth / nTotal;
			pLabel.width = nTotalWidth;
			pLabel.x = nTotalWidth * nButton;
			pLabel.y = ((nHeight - pLabel.height - nForegroundSkinHeight + BUTTON_GAP) / 2) + nForegroundSkinHeight;
		}
		
		// Called when the nagivation bar resizes
		protected function OnResize(event:Event):void
		{
			// Update our size based on our parent container
			width = (parent as Form).attributes.width;
			height = (parent as Form).attributes.height;
			
			// Update the skin size
			if (m_pMainSkin != null)
			{
				m_pMainSkin.width = width + MAIN_SKIN_PADDING;
				m_pMainSkin.height = height;
			}

			// Update the visual components
			var nForegroundSkinHeight:int = 0;
			for (var nButton:int = 0; nButton < m_pButtonNames.length; ++nButton)
			{
				// Set the background skin positions
				if (m_pBackgroundSkinUp[nButton] != null)
				{
					SetBackgroundSkinPosition(nButton, m_pButtonNames.length, width, height, m_pBackgroundSkinUp[nButton]);
				}
				if (m_pBackgroundSkinDown[nButton] != null)
				{
					SetBackgroundSkinPosition(nButton, m_pButtonNames.length, width, height, m_pBackgroundSkinDown[nButton]);
				}
				if (m_pBackgroundSkinDisabled[nButton] != null)
				{
					SetBackgroundSkinPosition(nButton, m_pButtonNames.length, width, height, m_pBackgroundSkinDisabled[nButton]);
				}
				
				// Set the foreground skin positions
				if ((m_pForegroundSkinWidths[nButton] != null) || (m_pForegroundSkinHeights[nButton] != null))
				{
					if (m_pForegroundSkinUp[nButton] != null)
					{
						nForegroundSkinHeight = SetForegroundSkinPosition(nButton, m_pButtonNames.length, width, height, 
							m_pForegroundSkinUp[nButton]);
					}
					if (m_pForegroundSkinDown[nButton] != null)
					{
						nForegroundSkinHeight = SetForegroundSkinPosition(nButton, m_pButtonNames.length, width, height,
							m_pForegroundSkinDown[nButton]);
					}
					if (m_pForegroundSkinDisabled[nButton] != null)
					{
						nForegroundSkinHeight = SetForegroundSkinPosition(nButton, m_pButtonNames.length, width, height,
							m_pForegroundSkinDisabled[nButton]);
					}
				}
				
				// Set the label position
				SetLabelPosition(nButton, m_pButtonNames.length, width, height, nForegroundSkinHeight);
			}
		}

		// Called when the button list has been received from the server
		public function UpdateButtons(pServerButtons:Array):void
		{
			// Walk our array of buttons
			var nClientButton:int, nServerButton:int, pLabel:UILabel;
			for (nClientButton = 0; nClientButton < m_pButtonNames.length; ++nClientButton)
			{
				// Walk the server's array of buttons
				for (nServerButton = 0; nServerButton < pServerButtons.length; ++nServerButton)
				{
					// Check for a match
					var pServerButton:Elixys.JSON.State.Button = pServerButtons[nServerButton] as Elixys.JSON.State.Button;
					if (m_pButtonNames[nClientButton] == pServerButton.ID)
					{
						// Show the label and enable or disable the button
						(m_pButtonLabels[nClientButton] as UILabel).visible = true;
						m_pButtonEnabled[nClientButton] = pServerButton.Enabled;
						break;
					}
				}
				
				// Hide the button if no match
				if (nServerButton == pServerButtons.length)
				{
					(m_pButtonLabels[nClientButton] as UILabel).visible = false;
				}
			}
			
			// Update the button states
			UpdateButtonStates();
		}

		// Updates the state of each button
		protected function UpdateButtonStates():void
		{
			// Walk our array of buttons
			for (var nButton:int = 0; nButton < m_pButtonEnabled.length; ++nButton)
			{
				// Determine skin visibility
				var bUp:Boolean, bDown:Boolean, bDisabled:Boolean, nTextColor:uint;
				var pLabel:UILabel = m_pButtonLabels[nButton] as UILabel;
				if (pLabel.visible)
				{
					// Set the enabled or disabled state
					if (m_pButtonEnabled[nButton])
					{
						bUp = true;
						bDown = false;
						bDisabled = false;
						nTextColor = m_nEnabledText;
					}
					else
					{
						bUp = false;
						bDown = false;
						bDisabled = true;
						nTextColor = m_nDisabledText;
					}
				}
				else
				{
					// Button is not visible
					bUp = false;
					bDown = false;
					bDisabled = false;
					nTextColor = m_nDisabledText;
				}

				// Set background skin visibility
				if (m_pBackgroundSkinUp[nButton] != null)
				{
					(m_pBackgroundSkinUp[nButton] as MovieClip).visible = bUp;
				}
				if (m_pBackgroundSkinDown[nButton] != null)
				{
					(m_pBackgroundSkinDown[nButton] as MovieClip).visible = bDown;
				}
				if (m_pBackgroundSkinDisabled[nButton] != null)
				{
					(m_pBackgroundSkinDisabled[nButton] as MovieClip).visible = bDisabled;
				}

				// Set foreground skin visibility
				if (m_pForegroundSkinUp[nButton] != null)
				{
					(m_pForegroundSkinUp[nButton] as MovieClip).visible = bUp;
				}
				if (m_pForegroundSkinDown[nButton] != null)
				{
					(m_pForegroundSkinDown[nButton] as MovieClip).visible = bDown;
				}
				if (m_pForegroundSkinDisabled[nButton] != null)
				{
					(m_pForegroundSkinDisabled[nButton] as MovieClip).visible = bDisabled;
				}
				
				// Set text color
				pLabel.textColor = nTextColor;
			}
		}

		/***
		 * Member variables
		 **/
		
		// Main background skin
		protected var m_pMainSkin:MovieClip;
		
		/// Navigation bar buttons
		protected var m_pButtonNames:Array = new Array();
		protected var m_pButtonLabels:Array = new Array();
		protected var m_pButtonEnabled:Array = new Array();
		protected var m_pForegroundSkinWidths:Array = new Array();
		protected var m_pForegroundSkinHeights:Array = new Array();
		protected var m_pForegroundSkinUp:Array = new Array();
		protected var m_pForegroundSkinDown:Array = new Array();
		protected var m_pForegroundSkinDisabled:Array = new Array();
		protected var m_pBackgroundSkinUp:Array = new Array();
		protected var m_pBackgroundSkinDown:Array = new Array();
		protected var m_pBackgroundSkinDisabled:Array = new Array();
		
		// Gap between the foreground skin and text
		protected static var BUTTON_GAP:int = 5;
		
		// Something is wrong with one of the assets so this is a quick fix
		protected static var MAIN_SKIN_PADDING:int = 8;

		// Button text colors
		protected var m_nEnabledText:uint = 0;
		protected var m_nDisabledText:uint = 0;
	}
}
