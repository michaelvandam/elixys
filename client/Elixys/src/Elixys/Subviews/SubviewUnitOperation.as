package Elixys.Subviews
{
	import Elixys.Assets.Constants;
	import Elixys.Assets.Styling;
	import Elixys.Extended.Form;
	import Elixys.Extended.Input;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Components.ComponentCassette;
	import Elixys.JSON.Components.Components;
	import Elixys.JSON.State.Reagent;
	import Elixys.JSON.State.Sequence;
	import Elixys.JSON.State.SequenceComponent;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.geom.Point;
	import flash.text.TextFormatAlign;

	// This unit operation base class is an extension of the base subview class
	public class SubviewUnitOperation extends SubviewBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewUnitOperation(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										sComponentType:String, attributes:Attributes)
		{
			// Call the base constructor
			super(screen, sMode, pElixys, sComponentType, nButtonWidth, VIEW_UNITOPERATION, 
				EDIT_UNITOPERATION, RUN_UNITOPERATION, attributes);

			// Get references to the view components
			m_pUnitOperationNumber = UILabel(findViewById("unitoperationnumber"));
			m_pUnitOperationName = UILabel(findViewById("unitoperationname"));
			m_pUnitOperationContainer = Form(findViewById("unitoperationcontainer"));

			// Add the unit operation number background skin
			m_pUnitOperationNumberBackground = AddSkinAt(sequencer_titleBar_mc, 0);

			// Get references to the component fields
			m_pComponentClass = Components.GetComponentClass(sComponentType);
			m_nComponentFieldCount = m_pComponentClass.FIELDCOUNT;
			m_pComponentFieldLabels = m_pComponentClass.FIELDLABELS;
			m_pComponentFieldTypes = m_pComponentClass.FIELDTYPES;
			m_pComponentFieldUnits = m_pComponentClass.FIELDUNITS;
			m_pComponentFieldProperties = m_pComponentClass.FIELDPROPERTIES;
		
			// Initialize the fields
			var nIndex:int, pLabel:UILabel;
			for (nIndex = 0; nIndex < m_nComponentFieldCount; ++nIndex)
			{
				// Create label
				pLabel = AddLabel("GothamMedium", 14, TextFormatAlign.LEFT);
				pLabel.text = m_pComponentFieldLabels[nIndex];
				m_pFieldLabels.push(pLabel);
				
				// Create contents
				switch (m_pComponentFieldTypes[nIndex])
				{
					case Constants.TYPE_DROPDOWN:
						m_pFieldContents.push(CreateDropdown());
						break;
					
					case Constants.TYPE_INPUT:
						m_pFieldContents.push(CreateInputControl());
						break;
					
					case Constants.TYPE_MULTILINEINPUT:
						m_pFieldContents.push(CreateMultilineInput());
						break;
					
					case Constants.TYPE_CHECKBOX:
						m_pFieldContents.push(CreateCheckbox());
						break;
					
					case Constants.TYPE_CHECKBOXINPUT:
						m_pFieldContents.push(CreateCheckboxInput());
						break;
				}
				
				// Create units label
				pLabel = AddLabel("GothamMedium", 14, TextFormatAlign.LEFT);
				pLabel.text = m_pComponentFieldUnits[nIndex];
				pLabel.textColor = Styling.AS3Color(Styling.TEXT_GRAY4);
				m_pFieldUnits.push(pLabel);

				// Create error label
				pLabel = AddLabel("GothamMedium", 14, TextFormatAlign.CENTER);
				pLabel.textColor = Styling.AS3Color(Styling.TEXT_RED);
				m_pFieldErrors.push(pLabel);
			}

			// Initialize the layout
			AdjustPositions();
		}

		/***
		 * Member functions
		 **/
		
		// Updates the sequence
		public override function UpdateSequence(pSequence:Sequence):void
		{
			// Call the base implementation and update
			super.UpdateSequence(pSequence);
			Update();
		}

		// Updates the component
		public override function UpdateComponent(pComponent:ComponentBase):void
		{
			// Cast to a real component, validate and update
			m_pComponent = new m_pComponentClass(null, pComponent);
			m_pComponent.Validate();
			Update();
		}
		
		// Updates the subview
		protected function Update():void
		{
			// Make sure we have both a sequence and component
			if ((m_pSequence == null) || (m_pComponent == null))
			{
				return;
			}
			
			// Update the unit operation number and name
			var nUnitOperationIndex:int = 0, nIndex:int, pSequenceComponent:SequenceComponent;
			for (nIndex = 0; nIndex < m_pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pSequenceComponent = m_pSequence.Components[nIndex] as SequenceComponent;
				if (pSequenceComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					continue;
				}
				
				// Check for the current component
				if (pSequenceComponent.ID == m_pComponent.ID)
				{
					break;
				}
				else
				{
					++nUnitOperationIndex;
				}
			}
			m_pUnitOperationNumber.text = (nUnitOperationIndex + 1).toString();
			m_pUnitOperationNumber.width = width;
			m_pUnitOperationName.text = m_pComponent.ComponentType;

			// Iterate over each field
			var pFields:Array;
			for (nIndex = 0; nIndex < m_nComponentFieldCount; ++nIndex)
			{
				// Set the field contents
				switch (m_pComponentFieldTypes[nIndex])
				{
					case Constants.TYPE_DROPDOWN:
						SetDropdown(m_pFieldContents[nIndex], m_pComponent[m_pComponentFieldProperties[nIndex]]);
						break;
					
					case Constants.TYPE_INPUT:
						SetInput(m_pFieldContents[nIndex], m_pComponent[m_pComponentFieldProperties[nIndex]]);
						break;

					case Constants.TYPE_MULTILINEINPUT:
						SetMultilineInput(m_pFieldContents[nIndex], m_pComponent[m_pComponentFieldProperties[nIndex]]);
						break;

					case Constants.TYPE_CHECKBOX:
						SetCheckbox(m_pFieldContents[nIndex], m_pComponent[m_pComponentFieldProperties[nIndex]]);
						break;
					
					case Constants.TYPE_CHECKBOXINPUT:
						pFields = (m_pComponentFieldProperties[nIndex] as String).split("|");
						SetCheckboxInput(m_pFieldContents[nIndex], m_pComponent[pFields[0]], m_pComponent[pFields[1]]);
						break;
				}
			
				// Set the error text
				if (m_pComponentFieldTypes[nIndex] == Constants.TYPE_CHECKBOXINPUT)
				{
					if (m_pComponent[pFields[0] + "Error"] != "")
					{
						(m_pFieldErrors[nIndex] as UILabel).text = m_pComponent[pFields[0] + "Error"];
					}
					else if (m_pComponent[pFields[1] + "Error"] != "")
					{
						(m_pFieldErrors[nIndex] as UILabel).text = m_pComponent[pFields[1] + "Error"];
					}
				}
				else
				{
					(m_pFieldErrors[nIndex] as UILabel).text = m_pComponent[m_pComponentFieldProperties[nIndex] + "Error"];
				}
			}
			
			// Adjust the layout
			AdjustPositions();
		}

		// Adjusts the view component positions
		protected function AdjustPositions():void
		{
			// Adjust the unit operation number and background skin
			m_pUnitOperationNumber.width = m_pUnitOperationNumber.textWidth + 8;
			var pSubviewPoint:Point = globalToLocal(m_pUnitOperationNumber.localToGlobal(
				new Point(m_pUnitOperationNumber.x, m_pUnitOperationNumber.y)));
			m_pUnitOperationNumberBackground.width = m_pUnitOperationNumber.width + 
				(2 * UNITOPERATIONHEADERPADDING);
			m_pUnitOperationNumberBackground.height = m_pUnitOperationNumber.height + 
				(2 * UNITOPERATIONHEADERPADDING);
			m_pUnitOperationNumberBackground.x = pSubviewPoint.x - UNITOPERATIONHEADERPADDING;
			m_pUnitOperationNumberBackground.y = pSubviewPoint.y - UNITOPERATIONHEADERPADDING;
			
			// Set the field positions
			var pLocal:Point = globalToLocal(m_pUnitOperationContainer.localToGlobal(new Point(0, 0)));
			var nOffsetX:Number = pLocal.x, nOffsetY:Number = pLocal.y, 
				nWidth:Number = m_pUnitOperationContainer.attributes.width - (HORIZONTALGAP * 3);
			var nLabelWidth:Number = nWidth * LABELPERCENTWIDTH / 100,
				nContentWidth:Number = nWidth * CONTENTSPERCENTWIDTH / 100,
				nUnitWidth:Number = nWidth * UNITSPERCENTWIDTH / 100,
				nErrorWidth:Number = nWidth * ERRORSPERCENTWIDTH / 100,
				nRowHeight:Number = m_pUnitOperationContainer.attributes.height * ROWPERCENTHEIGHT / 100;
			if (nRowHeight > (m_pUnitOperationContainer.attributes.height / m_nComponentFieldCount))
			{
				nRowHeight = m_pUnitOperationContainer.attributes.height / m_nComponentFieldCount;
			}
			var nIndex:int, pLabel:UILabel, nActualHeight:Number;
			for (nIndex = 0; nIndex < m_nComponentFieldCount; ++nIndex)
			{
				// Adjust the label
				pLabel = m_pFieldLabels[nIndex] as UILabel;
				pLabel.x = nOffsetX;
				pLabel.y = nOffsetY + ((nRowHeight - pLabel.height) / 2);
				nOffsetX += nLabelWidth + HORIZONTALGAP;
				
				// Adjust the contents
				switch (m_pComponentFieldTypes[nIndex])
				{
					case Constants.TYPE_DROPDOWN:
						AdjustDropdown(m_pFieldContents[nIndex], nContentWidth, nRowHeight, nOffsetX, nOffsetY);
						break;
					
					case Constants.TYPE_INPUT:
						AdjustInput(m_pFieldContents[nIndex], nContentWidth, nRowHeight, nOffsetX, nOffsetY);
						break;

					case Constants.TYPE_MULTILINEINPUT:
						nActualHeight = AdjustMultilineInput(m_pFieldContents[nIndex], nContentWidth + 
							HORIZONTALGAP + nUnitWidth + HORIZONTALGAP + nErrorWidth, nRowHeight, nOffsetX, nOffsetY);
						break;

					case Constants.TYPE_CHECKBOX:
						AdjustCheckbox(m_pFieldContents[nIndex], nContentWidth, nRowHeight, nOffsetX, nOffsetY);
						break;
					
					case Constants.TYPE_CHECKBOXINPUT:
						AdjustCheckboxInput(m_pFieldContents[nIndex], nContentWidth, nRowHeight, nOffsetX, nOffsetY);
						break;
				}
				nOffsetX += nContentWidth + HORIZONTALGAP;
				
				// Adjust the units label
				pLabel = m_pFieldUnits[nIndex] as UILabel;
				pLabel.x = nOffsetX;
				pLabel.y = nOffsetY + ((nRowHeight - pLabel.height) / 2);
				nOffsetX += nUnitWidth + HORIZONTALGAP;
				
				// Adjust the error label
				pLabel = m_pFieldErrors[nIndex] as UILabel;
				pLabel.x = nOffsetX;
				pLabel.y = nOffsetY + ((nRowHeight - pLabel.height) / 2);
				
				// Adjust the offsets
				nOffsetX = pLocal.x;
				if ((m_pComponentFieldTypes[nIndex] == Constants.TYPE_MULTILINEINPUT) &&
					(nActualHeight > nRowHeight))
				{
					nOffsetY += nActualHeight;
				}
				else
				{
					nOffsetY += nRowHeight;
				}
			}

			// Update the input area of interest
			m_nInputAreaOfInterestTop = m_pUnitOperationNumber.getBounds(stage).top;
			m_nInputAreaOfInterestBottom = m_pUnitOperationContainer.getBounds(stage).bottom;
		}

		// Creates a dropdown field
		protected function CreateDropdown():*
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					return AddLabel("GothamBold", 18, TextFormatAlign.LEFT);
					
				case Constants.EDIT:
					return null;
					
				default:
					return null;
			}
		}

		// Sets the dropdown field contents
		protected function SetDropdown(pDropdown:*, pContents:*):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					if (pContents is Reagent)
					{
						(pDropdown as UILabel).text = (pContents as Reagent).Name;
					}
					else
					{
						(pDropdown as UILabel).text = pContents.toString();
					}
					break;
				
				case Constants.EDIT:
					break;
			}
		}
		
		// Adust the dropdown field position
		protected function AdjustDropdown(pDropdown:*, nWidth:Number, nRowHeight:Number, nX:Number, nY:Number):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = pDropdown as UILabel;
					pLabel.x = nX + (nWidth - pLabel.width);
					pLabel.y = nY + ((nRowHeight - pLabel.height) / 2);
					break;
				
				case Constants.EDIT:
					break;
			}
		}

		// Creates an input field
		protected function CreateInputControl():*
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					return AddLabel("GothamBold", 18, TextFormatAlign.LEFT);
					
				case Constants.EDIT:
					return AddInput(22, Styling.TEXT_BLACK, Constants.RETURNKEYLABEL_NEXT);
					
				default:
					return null;
			}
		}

		// Sets the input field contents
		protected function SetInput(pInput:*, pContents:*):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					(pInput as UILabel).text = pContents.toString();
					break;
					
				case Constants.EDIT:
					(pInput as Input).text = pContents.toString();
					break;
			}
		}

		// Adust the input field position
		protected function AdjustInput(pInput:*, nWidth:Number, nRowHeight:Number, nX:Number, nY:Number):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = pInput as UILabel;
					pLabel.x = nX + (nWidth - pLabel.width);
					pLabel.y = nY + ((nRowHeight - pLabel.height) / 2);
					break;

				case Constants.EDIT:
					var pInputVar:Input = pInput as Input;
					pInputVar.FixWidth = nWidth;
					pInputVar.FixHeight = pInputVar.inputField.height;
					pInputVar.FixX = nX;
					pInputVar.FixY = nY + ((nRowHeight - pInputVar.height) / 2);
					break;
			}
		}

		// Creates an multiline input field
		protected function CreateMultilineInput():*
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					return AddLabel("GothamBold", 18, TextFormatAlign.LEFT);
					
				case Constants.EDIT:
					return null;
					
				default:
					return null;
			}
		}
		
		// Sets the multiline input field contents
		protected function SetMultilineInput(pInput:*, pContents:*):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					(pInput as UILabel).text = pContents.toString();
					break;
				
				case Constants.EDIT:
					break;
			}
		}
		
		// Adust the multiline input field position
		protected function AdjustMultilineInput(pInput:*, nWidth:Number, nRowHeight:Number, nX:Number, nY:Number):Number
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = pInput as UILabel;
					pLabel.fixwidth = nWidth;
					pLabel.x = nX;
					pLabel.y = nY;
					if (pLabel.numLines == 1)
					{
						pLabel.y += (nRowHeight - pLabel.height) / 2;
					}
					return pLabel.height;
				
				case Constants.EDIT:
					return 0;
			}
			return 0;
		}
		
		// Creates a checkbox field
		protected function CreateCheckbox():*
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					return AddLabel("GothamBold", 18, TextFormatAlign.LEFT);
					
				case Constants.EDIT:
					return null;
					
				default:
					return null;
			}
		}

		// Sets the checkbox field contents
		protected function SetCheckbox(pCheckbox:*, pContents:*):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					(pCheckbox as UILabel).text = pContents ? "YES" : "NO";
					break;
				
				case Constants.EDIT:
					break;
			}
		}
		
		// Adust the checkbox field position
		protected function AdjustCheckbox(pCheckbox:*, nWidth:Number, nRowHeight:Number, nX:Number, nY:Number):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = pCheckbox as UILabel;
					pLabel.x = nX + (nWidth - pLabel.width);
					pLabel.y = nY + ((nRowHeight - pLabel.height) / 2);
					break;
				
				case Constants.EDIT:
					break;
			}
		}

		// Creates a checkbox and input field
		protected function CreateCheckboxInput():*
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					return AddLabel("GothamBold", 18, TextFormatAlign.LEFT);
					
				case Constants.EDIT:
					return null;
					
				default:
					return null;
			}
		}

		// Sets the checkbox-input field contents
		protected function SetCheckboxInput(pCheckboxInput:*, pCheckBoxContents:*, pInputContents:*):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					if (Boolean(pCheckBoxContents))
					{
						(pCheckboxInput as UILabel).text = pInputContents.toString();
					}
					else
					{
						(pCheckboxInput as UILabel).text = "NO";
					}
					break;
				
				case Constants.EDIT:
					break;
			}
		}
		
		// Adust the checkbox-input field position
		protected function AdjustCheckboxInput(pCheckboxInput:*, nWidth:Number, nRowHeight:Number, nX:Number, nY:Number):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = pCheckboxInput as UILabel;
					pLabel.x = nX + (nWidth - pLabel.width);
					pLabel.y = nY + ((nRowHeight - pLabel.height) / 2);
					break;
				
				case Constants.EDIT:
					break;
			}
		}

		/*
		// Called when a text control receives focus
		public function OnTextFocusIn(event:FocusEvent):void
		{
			/*
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
			/*
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
		
		/*
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

		// View react XML
		protected static const VIEW_UNITOPERATION:XML = 
			<columns gapH="0" widths="4%,5%,82%,9%">
				<frame />
				<rows gapV="0" heights="8%,92%">
					<frame alignV="centre">
						<label id="unitoperationnumber" useEmbedded="true">
							<font face="GothamMedium" color={Styling.TEXT_WHITE} size="14" />
						</label>
					</frame>
				</rows>
				<rows gapV="0" heights="8%,88%,4%">
					<frame alignV="centre">
						<label id="unitoperationname" useEmbedded="true">
							<font face="GothamBold" color={Styling.TEXT_BLACK} size="14" />
						</label>
					</frame>
					<frame id="unitoperationcontainer" />
				</rows>
			</columns>;

		// Edit react XML
		protected static const EDIT_UNITOPERATION:XML = 
			<columns gapH="0" widths="4%,5%,82%,9%">
				<frame />
				<rows gapV="0" heights="8%,92%">
					<frame alignV="centre">
						<label id="unitoperationnumber" useEmbedded="true">
							<font face="GothamMedium" color={Styling.TEXT_WHITE} size="14" />
						</label>
					</frame>
				</rows>
				<rows gapV="0" heights="8%,88%,4%">
					<frame alignV="centre">
						<label id="unitoperationname" useEmbedded="true">
							<font face="GothamBold" color={Styling.TEXT_BLACK} size="14" />
						</label>
					</frame>
					<frame id="unitoperationcontainer" />
				</rows>
			</columns>;

		// Run react XML
		protected static const RUN_UNITOPERATION:XML = 
			<columns gapH="0" widths="4%,5%,82%,9%">
				<frame />
				<rows gapV="0" heights="8%,92%">
					<frame alignV="centre">
						<label id="unitoperationnumber" useEmbedded="true">
							<font face="GothamMedium" color={Styling.TEXT_WHITE} size="14" />
						</label>
					</frame>
				</rows>
				<rows gapV="0" heights="8%,88%,4%">
					<frame alignV="centre">
						<label id="unitoperationname" useEmbedded="true">
							<font face="GothamBold" color={Styling.TEXT_BLACK} size="14" />
						</label>
					</frame>
					<frame id="unitoperationcontainer" />
				</rows>
			</columns>;
		
		// View components
		protected var m_pUnitOperationNumber:UILabel;
		protected var m_pUnitOperationNumberBackground:MovieClip;
		protected var m_pUnitOperationName:UILabel;
		protected var m_pUnitOperationContainer:Form;

		// Field variables
		protected var m_pComponentClass:Class;
		protected var m_nComponentFieldCount:int;
		protected var m_pComponentFieldLabels:Array;
		protected var m_pComponentFieldTypes:Array;
		protected var m_pComponentFieldUnits:Array;
		protected var m_pComponentFieldProperties:Array;
		protected var m_pFieldLabels:Array = new Array();
		protected var m_pFieldContents:Array = new Array();
		protected var m_pFieldUnits:Array = new Array();
		protected var m_pFieldErrors:Array = new Array();

		// Component from server
		protected var m_pComponent:*;
		
		// Constants
		protected static const UNITOPERATIONHEADERPADDING:int = 5;
		protected static const HORIZONTALGAP:int = 10;
		protected static const LABELPERCENTWIDTH:int = 30;
		protected static const CONTENTSPERCENTWIDTH:int = 25;
		protected static const UNITSPERCENTWIDTH:int = 20;
		protected static const ERRORSPERCENTWIDTH:int = 25;
		protected static const ROWPERCENTHEIGHT:int = 15;
	}
}
