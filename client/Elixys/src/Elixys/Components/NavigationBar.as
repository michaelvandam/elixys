package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.ButtonEvent;
	import Elixys.Extended.*;
	import Elixys.JSON.State.Button;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
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
				if ((pButtonXML.@blank.length() > 0) && (pButtonXML.@blank[0] == "true"))
				{
					m_pButtonNames.push("");
					m_pForegroundSkinHeights.push(0);
					m_pForegroundSkinWidths.push(0);
					m_pButtonFontFaces.push("");
					m_pButtonFontSizes.push("");
					m_pButtonFontEnabledColor.push(0);
					m_pButtonFontDisabledColor.push(0);
					pForegroundSkinUpName.push("");
					pForegroundSkinDownName.push("");
					pForegroundSkinDisabledName.push("");
					pBackgroundSkinUpName.push("");
					pBackgroundSkinDownName.push("");
					pBackgroundSkinDisabledName.push("");
					m_pButtonBlankFlags.push(true);
				}
				else
				{
					m_pButtonNames.push(pButtonXML.@name[0]);
					m_pBackgroundSkinHeights.push(pButtonXML.@backgroundskinheightpercent[0]);
					m_pBackgroundSkinWidths.push(pButtonXML.@backgroundskinwidthpercent[0]);
					m_pForegroundSkinHeights.push(pButtonXML.@foregroundskinheightpercent[0]);
					m_pForegroundSkinWidths.push(pButtonXML.@foregroundskinwidthpercent[0]);
					m_pButtonFontFaces.push(pButtonXML.@fontFace[0]);
					m_pButtonFontSizes.push(pButtonXML.@fontSize[0]);
					m_pButtonFontEnabledColor.push(Styling.AS3Color(pButtonXML.@enabledTextColor[0]));
					m_pButtonFontDisabledColor.push(Styling.AS3Color(pButtonXML.@disabledTextColor[0]));
					pForegroundSkinUpName.push(pButtonXML.@foregroundskinup[0]);
					pForegroundSkinDownName.push(pButtonXML.@foregroundskindown[0]);
					pForegroundSkinDisabledName.push(pButtonXML.@foregroundskindisabled[0]);
					pBackgroundSkinUpName.push(pButtonXML.@backgroundskinup[0]);
					pBackgroundSkinDownName.push(pButtonXML.@backgroundskindown[0]);
					pBackgroundSkinDisabledName.push(pButtonXML.@backgroundskindisabled[0]);
					m_pButtonBlankFlags.push(false);
				}
				
				// Buttons are disabled and require no selection by default
				m_pButtonEnabled.push(false);
				m_pButtonSelectionRequired.push(false);

				// Remove the node from the XML
				delete xml.children()[pButtonXML.childIndex()];
			}
			
			// Get the vertical offset and right padding
			if (xml.@verticaloffset.length() > 0)
			{
				m_nVerticalOffset = xml.@verticaloffset[0];
			}
			if (xml.@rightpadding.length() > 0)
			{
				m_nRightPadding = xml.@rightpadding[0];
			}
			
			// Call the base constructor
			super(screen, xml, attributes, row, inGroup);
			
			// Determine our current width and height
			var nWidth:int = FindWidth(screen);
			var nHeight:int = FindHeight(screen);

			// Set the background skin
			if (xml.@skin.length() > 0)
			{
				m_pMainSkin = Utils.AddSkin(getDefinitionByName(xml.@skin[0]) as Class, true, this,
					nWidth, nHeight);
			}

			// Create the visual components
			var nForegroundSkinHeight:int = 0, pSkinSize:Point, pSkinPosition:Point, pSkin:Sprite;
			for (var nButton:int = 0; nButton < pButtonText.length; ++nButton)
			{
				// Create the label
				m_pButtonLabels.push(Utils.AddLabel(pButtonText[nButton], this, m_pButtonFontFaces[nButton], 
					m_pButtonFontSizes[nButton], m_pButtonFontDisabledColor[nButton]));

				// Skip remaining steps for blank buttons
				if (m_pButtonBlankFlags[nButton])
				{
					m_pBackgroundSkinUp.push(null);
					m_pBackgroundSkinDown.push(null);
					m_pBackgroundSkinDisabled.push(null);
					m_pForegroundSkinUp.push(null);
					m_pForegroundSkinDown.push(null);
					m_pForegroundSkinDisabled.push(null);
					continue;
				}

				// Create the button background skins
				pSkinSize = CalculateBackgroundSkinSize(nButton, pButtonText.length, nWidth, nHeight);
				if (pBackgroundSkinUpName[nButton] != null)
				{
					pSkin = Utils.AddSkin(getDefinitionByName(pBackgroundSkinUpName[nButton]) as Class, true,
						this, pSkinSize.x, pSkinSize.y);
					pSkinPosition = CalculateBackgroundSkinPosition(nButton, pButtonText.length, nWidth,
						nHeight, pSkin);
					pSkin.x = pSkinPosition.x;
					pSkin.y = pSkinPosition.y;
					m_pBackgroundSkinUp.push(pSkin);
				}
				else
				{
					m_pBackgroundSkinUp.push(null);
				}
				if (pBackgroundSkinDownName[nButton] != null)
				{
					pSkin = Utils.AddSkin(getDefinitionByName(pBackgroundSkinDownName[nButton]) as Class, true,
						this, pSkinSize.x, pSkinSize.y);
					pSkinPosition = CalculateBackgroundSkinPosition(nButton, pButtonText.length, nWidth,
						nHeight, pSkin);
					pSkin.x = pSkinPosition.x;
					pSkin.y = pSkinPosition.y;
					m_pBackgroundSkinDown.push(pSkin);
				}
				else
				{
					m_pBackgroundSkinDown.push(null);
				}
				if (pBackgroundSkinDisabledName[nButton] != null)
				{
					pSkin = Utils.AddSkin(getDefinitionByName(pBackgroundSkinDisabledName[nButton]) as Class, true,
						this, pSkinSize.x, pSkinSize.y);
					pSkinPosition = CalculateBackgroundSkinPosition(nButton, pButtonText.length, nWidth,
						nHeight, pSkin);
					pSkin.x = pSkinPosition.x;
					pSkin.y = pSkinPosition.y;
					m_pBackgroundSkinDisabled.push(pSkin);
				}
				else
				{
					m_pBackgroundSkinDisabled.push(null);
				}
				
				// Create the foreground skins
				if ((m_pForegroundSkinWidths[nButton] != null) || (m_pForegroundSkinHeights[nButton] != null))
				{
					pSkinSize = CalculateForegroundSkinSize(nButton, pButtonText.length, nWidth, nHeight);
					if (pForegroundSkinUpName[nButton] != null)
					{
						pSkin = Utils.AddSkin(getDefinitionByName(pForegroundSkinUpName[nButton]) as Class, true,
							this, pSkinSize.x, pSkinSize.y);
						pSkinPosition = CalculateForegroundSkinPosition(nButton, pButtonText.length, nWidth,
							nHeight, pSkin);
						pSkin.x = pSkinPosition.x;
						pSkin.y = pSkinPosition.y;
						m_pForegroundSkinUp.push(pSkin);
						nForegroundSkinHeight = pSkin.height;
					}
					else
					{
						m_pForegroundSkinUp.push(null);
					}
					if (pForegroundSkinDownName[nButton] != null)
					{
						pSkin = Utils.AddSkin(getDefinitionByName(pForegroundSkinDownName[nButton]) as Class, true,
							this, pSkinSize.x, pSkinSize.y);
						pSkinPosition = CalculateForegroundSkinPosition(nButton, pButtonText.length, nWidth,
							nHeight, pSkin);
						pSkin.x = pSkinPosition.x;
						pSkin.y = pSkinPosition.y;
						m_pForegroundSkinDown.push(pSkin);
						nForegroundSkinHeight = pSkin.height;
					}
					else
					{
						m_pForegroundSkinDown.push(null);
					}
					if (pForegroundSkinDisabledName[nButton] != null)
					{
						pSkin = Utils.AddSkin(getDefinitionByName(pForegroundSkinDisabledName[nButton]) as Class, true,
							this, pSkinSize.x, pSkinSize.y);
						pSkinPosition = CalculateForegroundSkinPosition(nButton, pButtonText.length, nWidth,
							nHeight, pSkin);
						pSkin.x = pSkinPosition.x;
						pSkin.y = pSkinPosition.y;
						m_pForegroundSkinDisabled.push(pSkin);
						nForegroundSkinHeight = pSkin.height;
					}
					else
					{
						m_pForegroundSkinDisabled.push(null);
					}
				}
				else
				{
					m_pForegroundSkinUp.push(null);
					m_pForegroundSkinDown.push(null);
					m_pForegroundSkinDisabled.push(null);
				}

				// Set the label position
				SetLabelPosition(nButton, pButtonText.length, nWidth, nHeight, nForegroundSkinHeight);
			}
			
			// Add event listners
			stage.addEventListener(Event.RESIZE, OnResize);
			addEventListener(MouseEvent.MOUSE_DOWN, OnMouseDown);
		}

		/***
		 * Member functions
		 **/

		// Calculates the background skin size and position
		protected function CalculateBackgroundSkinSize(nButton:int, nButtonCount:int, nTotalWidth:int, nTotalHeight:int):Point
		{
			// Determine the skin width and height
			var nSkinWidth:Number = 0, nSkinHeight:Number = 0;
			var nButtonWidth:int = (nTotalWidth - m_nRightPadding) / nButtonCount;
			if (m_pBackgroundSkinWidths[nButton] != null)
			{
				nSkinWidth = nTotalWidth * m_pBackgroundSkinWidths[nButton] / 100;
			}
			else if (m_pBackgroundSkinHeights[nButton] != null)
			{
				nSkinHeight = nTotalHeight * m_pBackgroundSkinHeights[nButton] / 100;
			}
			else
			{
				nSkinWidth = nButtonWidth;
				nSkinHeight = nTotalHeight;
			}
			
			// Return the skin size
			return new Point(nSkinWidth, nSkinHeight);
		}
		protected function CalculateBackgroundSkinPosition(nButton:int, nButtonCount:int, nTotalWidth:Number, 
														   nTotalHeight:Number, pSkin:Sprite):Point
		{
			// Return the skin position
			var nButtonWidth:Number = (nTotalWidth - m_nRightPadding) / nButtonCount;
			return new Point((nButtonWidth * nButton) + ((nButtonWidth - pSkin.width) / 2),
				m_nVerticalOffset + ((nTotalHeight - pSkin.height) / 2));
		}

		// Calculates the foreground skin size and position
		protected function CalculateForegroundSkinSize(nButton:int, nButtonCount:int, nWidth:int, nHeight:int):Point
		{
			// Determine the skin width and height
			var nSkinWidth:Number = 0, nSkinHeight:Number = 0;
			var nButtonWidth:Number = (nWidth - m_nRightPadding) / nButtonCount;
			if (m_pForegroundSkinWidths[nButton] != null)
			{
				nSkinWidth = nButtonWidth * m_pForegroundSkinWidths[nButton] / 100;
			}
			else
			{
				nSkinHeight = nHeight * m_pForegroundSkinHeights[nButton] / 100;
			}
			
			// Return the skin size
			return new Point(nSkinWidth, nSkinHeight);
		}
		protected function CalculateForegroundSkinPosition(nButton:int, nButtonTotal:int, nTotalWidth:Number, 
														   nTotalHeight:Number, pSkin:Sprite):Point
		{
			// Get the text height
			var nTextHeight:int = 0;
			if (m_pButtonLabels.length > nButton)
			{
				nTextHeight = UILabel(m_pButtonLabels[nButton]).textHeight;
			}

			// Return the skin position
			var nButtonWidth:Number = (nTotalWidth - m_nRightPadding) / nButtonTotal;
			return new Point((nButtonWidth * nButton) + (nButtonWidth - pSkin.width) / 2,
				m_nVerticalOffset + ((nTotalHeight - nTextHeight - pSkin.height - BUTTON_GAP) / 2));
		}

		// Set the label position
		protected function SetLabelPosition(nButton:int, nButtonCount:int, nTotalWidth:int, 
											nTotalHeight:int, nForegroundSkinHeight:int):void
		{
			var pLabel:UILabel = m_pButtonLabels[nButton];
			var nButtonWidth:int = (nTotalWidth - m_nRightPadding) / nButtonCount;
			pLabel.width = nButtonWidth;
			pLabel.x = (nButtonWidth * nButton) + ((nButtonWidth - pLabel.textWidth) / 2);
			pLabel.y = m_nVerticalOffset + nForegroundSkinHeight +
				((nTotalHeight - pLabel.height - nForegroundSkinHeight + BUTTON_GAP) / 2);
		}
		
		// Called when the stage resizes
		protected function OnResize(event:Event):void
		{
			// Update our size based on our parent container
			width = (parent as Form).attributes.width;
			height = (parent as Form).attributes.height;
			
			// Update the skin size
			if (m_pMainSkin != null)
			{
				m_pMainSkin.width = width;
				m_pMainSkin.height = height;
			}
			
			// Update the visual components
			var nForegroundSkinHeight:int = 0, pSkinPosition:Point, pSkin:Sprite;
			for (var nButton:int = 0; nButton < m_pButtonNames.length; ++nButton)
			{
				// Set the background skin positions
				if (m_pBackgroundSkinUp[nButton] != null)
				{
					pSkin = m_pBackgroundSkinUp[nButton] as Sprite;
					pSkinPosition = CalculateBackgroundSkinPosition(nButton, m_pButtonNames.length, width, height, pSkin); 
					pSkin.x = pSkinPosition.x;
					pSkin.y = pSkinPosition.y;
				}
				if (m_pBackgroundSkinDown[nButton] != null)
				{
					pSkin = m_pBackgroundSkinDown[nButton] as Sprite;
					pSkinPosition = CalculateBackgroundSkinPosition(nButton, m_pButtonNames.length, width, height, pSkin); 
					pSkin.x = pSkinPosition.x;
					pSkin.y = pSkinPosition.y;
				}
				if (m_pBackgroundSkinDisabled[nButton] != null)
				{
					pSkin = m_pBackgroundSkinDisabled[nButton] as Sprite;
					pSkinPosition = CalculateBackgroundSkinPosition(nButton, m_pButtonNames.length, width, height, pSkin); 
					pSkin.x = pSkinPosition.x;
					pSkin.y = pSkinPosition.y;
				}
				
				// Set the foreground skin positions
				if ((m_pForegroundSkinWidths[nButton] != null) || (m_pForegroundSkinHeights[nButton] != null))
				{
					if (m_pForegroundSkinUp[nButton] != null)
					{
						pSkin = m_pForegroundSkinUp[nButton] as Sprite;
						pSkinPosition = CalculateForegroundSkinPosition(nButton, m_pButtonNames.length, width, height, pSkin); 
						pSkin.x = pSkinPosition.x;
						pSkin.y = pSkinPosition.y;
						nForegroundSkinHeight = pSkin.height;
					}
					if (m_pForegroundSkinDown[nButton] != null)
					{
						pSkin = m_pForegroundSkinDown[nButton] as Sprite;
						pSkinPosition = CalculateForegroundSkinPosition(nButton, m_pButtonNames.length, width, height, pSkin); 
						pSkin.x = pSkinPosition.x;
						pSkin.y = pSkinPosition.y;
						nForegroundSkinHeight = pSkin.height;
					}
					if (m_pForegroundSkinDisabled[nButton] != null)
					{
						pSkin = m_pForegroundSkinDisabled[nButton] as Sprite;
						pSkinPosition = CalculateForegroundSkinPosition(nButton, m_pButtonNames.length, width, height, pSkin); 
						pSkin.x = pSkinPosition.x;
						pSkin.y = pSkinPosition.y;
						nForegroundSkinHeight = pSkin.height;
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
				// Only show buttons that are not blank
				if (m_pButtonBlankFlags[nClientButton] != "false")
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
							m_pButtonSelectionRequired[nClientButton] = pServerButton.SelectionRequired;
							break;
						}
					}
				}
				
				// Hide the button if blank or no match
				if ((m_pButtonBlankFlags[nClientButton] == "false") || (nServerButton == pServerButtons.length))
				{
					(m_pButtonLabels[nClientButton] as UILabel).visible = false;
				}
			}
			
			// Update the button states
			UpdateButtonStates();
		}

		// Updates the selection index
		public function UpdateSelection(nSelectionID:int):void
		{
			// Remember the ID and update the button states
			m_nSelectionID = nSelectionID;
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
					if ((!m_pButtonSelectionRequired[nButton] || (m_nSelectionID != -1)) && m_pButtonEnabled[nButton])
					{
						if (nButton == m_nPressedButton)
						{
							bUp = false;
							bDown = true;
						}
						else
						{
							bUp = true;
							bDown = false;
						}
						bDisabled = false;
						nTextColor = m_pButtonFontEnabledColor[nButton];
					}
					else
					{
						bUp = false;
						bDown = false;
						bDisabled = true;
						nTextColor = m_pButtonFontDisabledColor[nButton];
					}
				}
				else
				{
					// Button is not visible
					bUp = false;
					bDown = false;
					bDisabled = false;
					nTextColor = m_pButtonFontDisabledColor[nButton];
				}

				// Set background skin visibility
				if (m_pBackgroundSkinUp[nButton] != null)
				{
					(m_pBackgroundSkinUp[nButton] as Sprite).visible = bUp;
				}
				if (m_pBackgroundSkinDown[nButton] != null)
				{
					(m_pBackgroundSkinDown[nButton] as Sprite).visible = bDown;
				}
				if (m_pBackgroundSkinDisabled[nButton] != null)
				{
					(m_pBackgroundSkinDisabled[nButton] as Sprite).visible = bDisabled;
				}

				// Set foreground skin visibility
				if (m_pForegroundSkinUp[nButton] != null)
				{
					(m_pForegroundSkinUp[nButton] as Sprite).visible = bUp;
				}
				if (m_pForegroundSkinDown[nButton] != null)
				{
					(m_pForegroundSkinDown[nButton] as Sprite).visible = bDown;
				}
				if (m_pForegroundSkinDisabled[nButton] != null)
				{
					(m_pForegroundSkinDisabled[nButton] as Sprite).visible = bDisabled;
				}
				
				// Set text color
				pLabel.textColor = nTextColor;
			}
		}

		// Called when the user presses the mouse button
		protected function OnMouseDown(event:MouseEvent):void
		{
			// Convert the click coordinates
			var pNavigationBarPoint:Point = globalToLocal(new Point(event.stageX, event.stageY));
			
			// Determine which button was clicked
			var nButtonWidth:int = (width - m_nRightPadding) / m_pButtonNames.length;
			var nButton:int = pNavigationBarPoint.x / nButtonWidth;

			// Make sure the button is visible and enabled
			if (!(m_pButtonLabels[nButton] as UILabel).visible || !(m_pButtonEnabled[nButton] as Boolean))
			{
				return;
			}

			// Listen for mouse up
			stage.addEventListener(MouseEvent.MOUSE_UP, OnMouseUp);

			// Set the pressed index and update
			m_nPressedButton = nButton;
			UpdateButtonStates();
		}

		// Called when the user releases the mouse button
		protected function OnMouseUp(event:MouseEvent):void
		{
			// Remove the event listener
			stage.removeEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
			
			// Make sure we have a pressed button
			if (m_nPressedButton == -1)
			{
				return;
			}
			
			// Check if the mouse was released over the same button that was initially clicked
			var pNavigationBarPoint:Point = globalToLocal(new Point(event.stageX, event.stageY));
			if ((pNavigationBarPoint.y > 0) && (pNavigationBarPoint.y < height))
			{
				var nButtonWidth:int = (width - m_nRightPadding) / m_pButtonNames.length;
				if ((pNavigationBarPoint.x > (m_nPressedButton * nButtonWidth)) &&
					(pNavigationBarPoint.x < ((m_nPressedButton + 1) * nButtonWidth)))
				{
					// Dispatch a click event
					dispatchEvent(new ButtonEvent(m_pButtonNames[m_nPressedButton]));
				}
			}
				
			// Clear the pressed index and update
			m_nPressedButton = -1;
			UpdateButtonStates();
		}

		/***
		 * Member variables
		 **/
		
		// Main background skin
		protected var m_pMainSkin:Sprite;
		
		/// Navigation bar buttons
		protected var m_pButtonNames:Array = new Array();
		protected var m_pButtonLabels:Array = new Array();
		protected var m_pButtonEnabled:Array = new Array();
		protected var m_pButtonSelectionRequired:Array = new Array();
		protected var m_pButtonFontFaces:Array = new Array();
		protected var m_pButtonFontSizes:Array = new Array();
		protected var m_pButtonFontEnabledColor:Array = new Array();
		protected var m_pButtonFontDisabledColor:Array = new Array();
		protected var m_pForegroundSkinWidths:Array = new Array();
		protected var m_pForegroundSkinHeights:Array = new Array();
		protected var m_pForegroundSkinUp:Array = new Array();
		protected var m_pForegroundSkinDown:Array = new Array();
		protected var m_pForegroundSkinDisabled:Array = new Array();
		protected var m_pBackgroundSkinWidths:Array = new Array();
		protected var m_pBackgroundSkinHeights:Array = new Array();
		protected var m_pBackgroundSkinUp:Array = new Array();
		protected var m_pBackgroundSkinDown:Array = new Array();
		protected var m_pBackgroundSkinDisabled:Array = new Array();
		protected var m_pButtonBlankFlags:Array = new Array();
		
		// Button vertical offset
		protected var m_nVerticalOffset:int = 0;
		
		// Gap between the foreground skin and text
		protected static var BUTTON_GAP:int = 8;
		
		// Padding to the right of our buttons
		protected var m_nRightPadding:int = 0;
		
		// Index of the currently pressed button or -1
		protected var m_nPressedButton:int = -1;

		// ID of the currently selected item
		protected var m_nSelectionID:int = -1;
	}
}
