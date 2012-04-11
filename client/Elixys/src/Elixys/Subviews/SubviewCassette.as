package Elixys.Subviews
{
	import Elixys.Assets.*;
	import Elixys.Extended.Form;
	import Elixys.Extended.Input;
	import Elixys.Interfaces.ITextBox;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Components.ComponentCassette;
	import Elixys.JSON.Configuration.Configuration;
	import Elixys.JSON.Configuration.DisallowedReagentPosition;
	import Elixys.JSON.State.Reagent;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.FocusEvent;
	import flash.events.KeyboardEvent;
	import flash.events.MouseEvent;
	import flash.events.SoftKeyboardEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextField;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.getQualifiedClassName;

	// This cassette subview is an extension of the subview base class
	public class SubviewCassette extends SubviewBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewCassette(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			// Call the base constructor
			super(screen, sMode, pElixys, ComponentCassette.COMPONENTTYPE, nButtonWidth, VIEW_CASSETTE, 
				EDIT_CASSETTE, RUN_CASSETTE, attributes);
			
			// Get references to the components and add event listeners
			m_pCassetteLabel = UILabel(findViewById("cassettelabel"));
			switch (m_sMode)
			{
				case Constants.VIEW:
					m_pReagentNameLabel = UILabel(findViewById("reagentnamelabel"));
					m_pReagentDescriptionLabel = UILabel(findViewById("reagentdescriptionlabel"));
					break;
				
				case Constants.EDIT:
					m_pReagentNameInput = Input(findViewById("reagentnameinput"));
					m_pReagentNameTextBox = m_pReagentNameInput.inputField as ITextBox;
					m_pReagentNameTextBox.addEventListener(FocusEvent.FOCUS_IN, OnTextFocusIn);
					m_pReagentNameTextBox.addEventListener(FocusEvent.FOCUS_OUT, OnTextFocusOut);
					m_pReagentNameTextBox.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_ACTIVATE, OnKeyboardChange);
					m_pReagentNameTextBox.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_DEACTIVATE, OnKeyboardChange);
					m_pReagentNameTextBox.addEventListener(KeyboardEvent.KEY_DOWN, OnReagentNameKeyDown);
					m_pReagentDescriptionInput = Input(findViewById("reagentdescriptioninput"));
					m_pReagentDescriptionTextBox = m_pReagentDescriptionInput.inputField as ITextBox;
					m_pReagentDescriptionTextBox.addEventListener(FocusEvent.FOCUS_IN, OnTextFocusIn);
					m_pReagentDescriptionTextBox.addEventListener(FocusEvent.FOCUS_OUT, OnTextFocusOut);
					m_pReagentDescriptionTextBox.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_ACTIVATE, OnKeyboardChange);
					m_pReagentDescriptionTextBox.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_DEACTIVATE, OnKeyboardChange);
					m_pReagentDescriptionTextBox.addEventListener(KeyboardEvent.KEY_DOWN, OnReagentDescriptionKeyDown);
					break;
			}
			m_pReagentContainer = Form(findViewById("reagentcontainer"));
			
			// Create the buttons
			for (var nIndex:int = 0; nIndex < REAGENTCOUNT; ++nIndex)
			{
				// Create the skins
				m_pUpSkins.push(AddSkinWidth(tools_btn_up, m_nButtonWidth));
				m_pDownSkins.push(AddSkinWidth(tools_btn_down, m_nButtonWidth));
				m_pDisabledSkins.push(AddSkinWidth(tools_btn_disabled, m_nButtonWidth));
				m_pActiveSkins.push(AddSkinWidth(tools_btn_active, m_nButtonWidth));

				// Create the labels
				m_pLabels.push(AddLabel(FONTFACE, FONTSIZE, TextFormatAlign.CENTER));
				
				// Create an initial hit area and enabled flag
				m_pHitAreas.push(new Rectangle());
				m_pEnabledFlags.push(true);
			}
			
			// Add event listeners
			addEventListener(MouseEvent.MOUSE_DOWN, OnMouseDown);
			
			// Initialize the button positions
			AdjustPositions();
		}
		
		/***
		 * Member functions
		 **/
		
		// Updates the component
		public override function UpdateComponent(pComponent:ComponentBase):void
		{
			// Ignore in run mode
			if (m_sMode == Constants.RUN)
			{
				return;
			}
			
			// Initialize the disallowed position reference
			if (m_pDisallowedReagentPositions == null)
			{
				m_pDisallowedReagentPositions = m_pElixys.GetConfiguration().DisallowedReagentPositions;
			}
			
			// Start with all reagents enabled
			var nIndex:int;
			for (nIndex = 0; nIndex < REAGENTCOUNT; ++nIndex)
			{
				m_pEnabledFlags[nIndex] = true;
			}

			// Disable any disallowed positions
			m_pComponent = new ComponentCassette(null, pComponent);
			for (nIndex = 0; nIndex < m_pDisallowedReagentPositions.length; ++nIndex)
			{
				var pDisallowedReagentPosition:DisallowedReagentPosition = 
					m_pDisallowedReagentPositions[nIndex] as DisallowedReagentPosition;
				if (m_pComponent.Reactor == pDisallowedReagentPosition.Cassette)
				{
					m_pEnabledFlags[pDisallowedReagentPosition.Reagent - 1] = false;
				}
			}

			// Press or release the buttons
			for (nIndex = 0; nIndex < REAGENTCOUNT; ++nIndex)
			{
				if (nIndex == m_nPressedReagent)
				{
					PressButton(nIndex);
				}
				else
				{
					ReleaseButton(nIndex);
				}
			}

			// Adjust the positions and selected reagent
			AdjustPositions();
			SelectReagent(m_nSelectedReagent);
		}
		
		// Adjust the component position
		protected function AdjustPositions():void
		{
			// Ignore in run mode
			if (m_sMode == Constants.RUN)
			{
				return;
			}

			// Update if our dimensions have changed
			if ((m_pReagentContainer.attributes.width != m_nLastWidth) ||
				(m_pReagentContainer.attributes.height != m_nLastHeight))
			{
				// Initialize offsets
				var nInitialOffsetX:Number = m_pReagentContainer.x + (m_pReagentContainer.attributes.width - 
					((m_pUpSkins[0] as MovieClip).width * 5) - (BUTTON_HORIZONTAL_GAP * 4)) / 2;
				var nOffsetX:Number = nInitialOffsetX;
				var nOffsetY:Number = m_pReagentContainer.y + (m_pReagentContainer.attributes.height - 
					((m_pUpSkins[0] as MovieClip).height * 4) - (BUTTON_VERTICAL_GAP * 3)) / 2;
				
				// Iterate over all 20 positions in the 5 x 4 grid
				var nIndex:int, pRectangle:Rectangle, pUpSkin:MovieClip, pDownSkin:MovieClip, 
					pActiveSkin:MovieClip, pDisabledSkin:MovieClip, pLabel:UILabel, nReagentIndex:int = 0;
				for (nIndex = 0; nIndex < 20; ++nIndex)
				{
					// Select for reagent positions
					switch (nIndex + 1)
					{
						case 1:
						case 2:
						case 4:
						case 5:
						case 7:
						case 9:
						case 12:
						case 14:
						case 17:
						case 18:
						case 19:
							// Set the skin positions
							pUpSkin = m_pUpSkins[nReagentIndex] as MovieClip;
							pDownSkin = m_pDownSkins[nReagentIndex] as MovieClip;
							pActiveSkin = m_pActiveSkins[nReagentIndex] as MovieClip;
							pDisabledSkin = m_pDisabledSkins[nReagentIndex] as MovieClip;
							pUpSkin.x = pDownSkin.x = pActiveSkin.x = pDisabledSkin.x = nOffsetX;
							pUpSkin.y = pDownSkin.y = pActiveSkin.y = pDisabledSkin.y = nOffsetY;
							
							// Set the label text and position
							pLabel = m_pLabels[nReagentIndex] as UILabel;
							pLabel.width = pUpSkin.width;
							pLabel.text = (nReagentIndex + 1).toString();
							pLabel.width = pLabel.textWidth + 5;
							pLabel.x = pUpSkin.x + ((pUpSkin.width - pLabel.width) / 2);
							pLabel.y = pUpSkin.y + ((pUpSkin.height - pLabel.height) / 2);

							// Set the hit area
							pRectangle = m_pHitAreas[nReagentIndex] as Rectangle;
							pRectangle.x = nOffsetX;
							pRectangle.y = nOffsetY;
							pRectangle.width = pUpSkin.width;
							pRectangle.height = pUpSkin.height;

							// Increment the reagent index
							++nReagentIndex;
					}
					if (((nIndex + 1) % 5) != 0)
					{
						nOffsetX += (m_pUpSkins[0] as MovieClip).width + BUTTON_HORIZONTAL_GAP;
					}
					else
					{
						nOffsetX = nInitialOffsetX;
						nOffsetY += (m_pUpSkins[0] as MovieClip).height + BUTTON_VERTICAL_GAP;
					}
				}

				// Update the input area of interest
				m_nInputAreaOfInterestTop = m_pCassetteLabel.getBounds(stage).top;
				m_nInputAreaOfInterestBottom = (m_pUpSkins[REAGENTCOUNT - 1] as MovieClip).getBounds(stage).bottom;

				// Remember the new dimensions
				m_nLastWidth = m_pReagentContainer.attributes.width;
				m_nLastHeight = m_pReagentContainer.attributes.height;
			}
		}

		// Selects the specified reagent
		protected function SelectReagent(nReagentIndex:int):void
		{
			// Set the label, name and description
			m_pCassetteLabel.text = "CASSETTE " + m_pComponent.Reactor + " : VIAL " + (nReagentIndex + 1).toString();
			if (m_pEnabledFlags[nReagentIndex])
			{
				switch (m_sMode)
				{
					case Constants.VIEW:
						m_pReagentNameLabel.text = (m_pComponent.Reagents[nReagentIndex] as Reagent).Name;
						var nMaxTextWidth:Number = (m_pReagentDescriptionLabel.parent as Form).attributes.width;
						m_pReagentDescriptionLabel.width = nMaxTextWidth;
						m_pReagentDescriptionLabel.text = (m_pComponent.Reagents[nReagentIndex] as Reagent).Description;
						if (m_pReagentDescriptionLabel.textWidth > nMaxTextWidth)
						{
							AddEllipsis(m_pReagentDescriptionLabel, nMaxTextWidth);
						}
						break;
					
					case Constants.EDIT:
						m_pReagentNameInput.text = (m_pComponent.Reagents[nReagentIndex] as Reagent).Name;
						m_pReagentNameTextBox.editable = true;
						m_pReagentNameTextBox.color = Styling.AS3Color(Styling.TEXT_BLACK);
						m_pReagentDescriptionInput.text = (m_pComponent.Reagents[nReagentIndex] as Reagent).Description;
						m_pReagentDescriptionTextBox.editable = true;
						m_pReagentDescriptionTextBox.color = Styling.AS3Color(Styling.TEXT_BLACK);
						break;
				}
			}
			else
			{
				switch (m_sMode)
				{
					case Constants.VIEW:
						m_pReagentNameLabel.text = "[Position not allowed]";
						m_pReagentDescriptionLabel.text = "";
						break;
					
					case Constants.EDIT:
						m_pReagentNameInput.text = "[Position not allowed]";
						m_pReagentNameTextBox.editable = false;
						m_pReagentNameTextBox.color = Styling.AS3Color(Styling.TEXT_GRAY5);
						m_pReagentDescriptionInput.text = "";
						m_pReagentDescriptionTextBox.editable = false;
						m_pReagentDescriptionTextBox.color = Styling.AS3Color(Styling.TEXT_GRAY5);
						break;
				}
			}
			
			// Select the new reagent
			var nOldReagent:int = m_nSelectedReagent;
			m_nSelectedReagent = nReagentIndex;
			ReleaseButton(nOldReagent);
			ReleaseButton(m_nSelectedReagent);
		}

		
		// Presses the specified button
		protected function PressButton(nIndex:int):void
		{
			(m_pUpSkins[nIndex] as MovieClip).visible = false;
			(m_pDownSkins[nIndex] as MovieClip).visible = true;
			(m_pDisabledSkins[nIndex] as MovieClip).visible = false;
			(m_pActiveSkins[nIndex] as MovieClip).visible = false;
			(m_pLabels[nIndex] as UILabel).textColor = PRESSEDTEXTCOLOR;
		}
		
		// Release the specified button
		protected function ReleaseButton(nIndex:int):void
		{
			var bUpVisible:Boolean = false, bDownVisible:Boolean = false, bActiveVisible:Boolean = false,
				bDisabledVisible:Boolean = false, nTextColor:uint = 0;
			if (m_pEnabledFlags[nIndex])
			{
				if (nIndex == m_nSelectedReagent)
				{
					bActiveVisible = true;
					nTextColor = ACTIVETEXTCOLOR;
				}
				else
				{
					bUpVisible = true;
					nTextColor = ENABLEDTEXTCOLOR;
				}
			}
			else
			{
				bDisabledVisible = true;
				nTextColor = DISABLEDTEXTCOLOR;
			}
			(m_pUpSkins[nIndex] as MovieClip).visible = bUpVisible;
			(m_pDownSkins[nIndex] as MovieClip).visible = bDownVisible;
			(m_pDisabledSkins[nIndex] as MovieClip).visible = bDisabledVisible;
			(m_pActiveSkins[nIndex] as MovieClip).visible = bActiveVisible;
			(m_pLabels[nIndex] as UILabel).textColor = nTextColor;
		}

		// Reduces the string width and adds ellipsis
		protected function AddEllipsis(pTextField:TextField, nMaxWidth:Number):void
		{
			if (pTextField.textWidth > nMaxWidth)
			{
				// Append the ellipsis
				pTextField.appendText("...");
				
				// Loop until the string is small enough
				while (pTextField.textWidth > nMaxWidth)
				{
					pTextField.replaceText(pTextField.text.length - 4, pTextField.text.length - 3, "");
				}
			}
		}

		// Called when the user presses the mouse button
		protected function OnMouseDown(event:MouseEvent):void
		{
			// Check for button clicks
			for (var nIndex:int = 0; nIndex < REAGENTCOUNT; ++nIndex)
			{
				if ((m_pHitAreas[nIndex] as Rectangle).contains(mouseX, mouseY))
				{
					// Ignore clicks on disabled buttons
					if (!m_pEnabledFlags[nIndex])
					{
						return;
					}
					
					// Press the button and wait for mouse up
					m_nPressedReagent = nIndex;
					PressButton(m_nPressedReagent);
					stage.addEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
					break;
				}
			}
		}
		
		// Called when the user releases the mouse button
		protected function OnMouseUp(event:MouseEvent):void
		{
			// Remove the event listener and release the button
			stage.removeEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
			ReleaseButton(m_nPressedReagent);
			
			// Check if the mouse was release over the same button that was initially clicked
			if ((m_pHitAreas[m_nPressedReagent] as Rectangle).contains(mouseX, mouseY))
			{
				// Select the reagent
				SelectReagent(m_nPressedReagent);
			}
			m_nPressedReagent = -1;
		}

		// Called when a text control receives focus
		public function OnTextFocusIn(event:FocusEvent):void
		{
			// Determine which input has the keyboard focus
			if (m_pReagentNameTextBox.containsInternally(event.target))
			{
				m_pKeyboardFocusTextBox = m_pReagentNameTextBox;
			}
			else if (m_pReagentDescriptionTextBox.containsInternally(event.target))
			{
				m_pKeyboardFocusTextBox = m_pReagentDescriptionTextBox;
			}
			
			// Remember the initial text
			m_sKeyboardFocusInitialText = m_pKeyboardFocusTextBox.text;
		}
		
		// Called when a text control loses focus
		public function OnTextFocusOut(event:FocusEvent):void
		{
			if (m_pKeyboardFocusTextBox != null)
			{
				// Has the value of the text input changed?
				if (m_pKeyboardFocusTextBox.text != m_sKeyboardFocusInitialText)
				{
					// Yes, so update and save the component
					OnTextValueChanged(m_pKeyboardFocusTextBox);
				}
				
				// Clear our pointer
				m_pKeyboardFocusTextBox = null;
			}
		}
		
		// Returns the item that currently has the keyboard focus
		public function KeyboardFocusTextArea():ITextBox
		{
			return m_pKeyboardFocusTextBox;
		}

		// Called when the soft keyboard actives or deactivates
		protected function OnKeyboardChange(event:SoftKeyboardEvent):void
		{
			// Pan the application
			m_pElixys.PanApplication(m_nInputAreaOfInterestTop, m_nInputAreaOfInterestBottom);
		}
		
		// Called when the user changes the text in one of our input fields
		protected function OnTextValueChanged(pFocusTarget:ITextBox):void
		{
			// Copy and update the selected reagent
			var pSelectedReagent:Reagent = new Reagent();
			pSelectedReagent.Copy(m_pComponent.Reagents[m_nSelectedReagent] as Reagent);
			if (m_pKeyboardFocusTextBox == m_pReagentNameTextBox)
			{
				pSelectedReagent.Name = m_pReagentNameTextBox.text;
			}
			
			// Post the reagent to the server
			PostReagent(pSelectedReagent);
		}

		// Called when the reagent name field receives a key down event
		protected function OnReagentNameKeyDown(event:KeyboardEvent):void
		{
			// Either tab or return moves the focus to the reagent description field
			if ((event.keyCode == Constants.CHAR_TAB) || (event.keyCode == Constants.CHAR_RETURN))
			{
				event.preventDefault();
				m_pReagentDescriptionTextBox.assignFocus();
			}
		}
		
		// Called when the reagent description field receives a key down event
		protected function OnReagentDescriptionKeyDown(event:KeyboardEvent):void
		{
			// Either tab or return moves the focus to the reagent name field
			if ((event.keyCode == Constants.CHAR_TAB) || (event.keyCode == Constants.CHAR_RETURN))
			{
				event.preventDefault();
				m_pReagentNameTextBox.assignFocus();
			}
		}

		/***
		 * Member variables
		 **/

		// View cassette XML
		protected static const VIEW_CASSETTE:XML = 
			<columns gapH="0" widths="6%,88%,6%">
				<frame />
				<rows background={Styling.APPLICATION_BACKGROUND} gapV="0" heights="2%,8%,10,18%,72%">
					<frame />
					<label id="cassettelabel" useEmbedded="true" alignH="left" alignV="centre">
						<font face="GothamBold" color={Styling.TEXT_BLUE2} size="16" />
					</label>
					<frame />
					<columns gapH="10" widths="17%,83%">
						<rows gapV="10">
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									NAME
								</font>
							</label>
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									DESCRIPTION
								</font>
							</label>
						</rows>
						<rows gapV="10">
							<label id="reagentnamelabel" useEmbedded="true" alignH="left" alignV="centre">
								<font face="GothamBold" color={Styling.TEXT_BLACK} size="16" />
							</label>
							<label id="reagentdescriptionlabel" useEmbedded="true" alignH="left" alignV="centre">
								<font face="GothamBold" color={Styling.TEXT_BLACK} size="16" />
							</label>
						</rows>
					</columns>
					<frame id="reagentcontainer" />
				</rows>
			</columns>;

		// Edit cassette XML
		protected static const EDIT_CASSETTE:XML = 
			<columns gapH="0" widths="6%,88%,6%">
				<frame />
				<rows background={Styling.APPLICATION_BACKGROUND} gapV="0" heights="2%,8%,10,18%,72%">
					<frame />
					<label id="cassettelabel" useEmbedded="true" alignH="left" alignV="centre">
						<font face="GothamBold" color={Styling.TEXT_BLUE2} size="16" />
					</label>
					<frame />
					<columns gapH="10" widths="17%,83%">
						<rows gapV="10">
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									NAME
								</font>
							</label>
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									DESCRIPTION
								</font>
							</label>
						</rows>
						<rows gapV="10" heights="50%,50%">
							<frame alignH="fill">
								<input id="reagentnameinput" alignH="fill" color={Styling.TEXT_GRAY1} 
										size="22" skin={getQualifiedClassName(TextInput_upSkin)} 
										returnKeyLabel={Constants.RETURNKEYLABEL_NEXT} />
							</frame>
							<frame alignH="fill">
								<input id="reagentdescriptioninput" alignH="fill" color={Styling.TEXT_GRAY1} 
										size="22" skin={getQualifiedClassName(TextInput_upSkin)} 
										returnKeyLabel={Constants.RETURNKEYLABEL_NEXT} />
							</frame>
						</rows>
					</columns>
					<frame id="reagentcontainer" />
				</rows>
			</columns>;

		// Run cassette XML
		protected static const RUN_CASSETTE:XML = 
			<frame />;
		
		// Cassette components
		protected var m_pCassetteLabel:UILabel;
		protected var m_pReagentNameLabel:UILabel;
		protected var m_pReagentDescriptionLabel:UILabel;
		protected var m_pReagentNameInput:Input;
		protected var m_pReagentNameTextBox:ITextBox;
		protected var m_pReagentDescriptionInput:Input;
		protected var m_pReagentDescriptionTextBox:ITextBox;
		protected var m_pReagentContainer:Form;

		// Cassette arrays
		protected var m_pUpSkins:Array = new Array();
		protected var m_pDownSkins:Array = new Array();
		protected var m_pDisabledSkins:Array = new Array();
		protected var m_pActiveSkins:Array = new Array();
		protected var m_pLabels:Array = new Array();
		protected var m_pHitAreas:Array = new Array();
		protected var m_pEnabledFlags:Array = new Array();

		// Keyboard focus variables
		protected var m_pKeyboardFocusTextBox:ITextBox;
		private var m_sKeyboardFocusInitialText:String = "";

		// Disallowed reagent positions
		protected var m_pDisallowedReagentPositions:Array;

		// Current cassette and selected reagent index
		protected var m_pComponent:ComponentCassette;
		protected var m_nSelectedReagent:int = 0;
		protected var m_nPressedReagent:int = -1;

		// Last know dimensions
		protected var m_nLastWidth:Number = 0;
		protected var m_nLastHeight:Number = 0;
		
		// Constants
		protected static const REAGENTCOUNT:int = 11;
		protected static const FONTFACE:String = "GothamBold";
		protected static const FONTSIZE:int = 34;
		protected static const ENABLEDTEXTCOLOR:uint = Styling.AS3Color(Styling.TEXT_GRAY2);
		protected static const DISABLEDTEXTCOLOR:uint = Styling.AS3Color(Styling.TEXT_GRAY7);
		protected static const ACTIVETEXTCOLOR:uint = Styling.AS3Color(Styling.TEXT_BLUE1);
		protected static const PRESSEDTEXTCOLOR:uint = Styling.AS3Color(Styling.TEXT_WHITE);
		protected static const BUTTON_HORIZONTAL_GAP:int = 10;
		protected static const BUTTON_VERTICAL_GAP:int = 10;
	}
}
