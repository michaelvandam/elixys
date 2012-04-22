package Elixys.Subviews
{
	import Elixys.Assets.Constants;
	import Elixys.Assets.Styling;
	import Elixys.Components.CheckBox;
	import Elixys.Events.ButtonEvent;
	import Elixys.Events.CheckBoxEvent;
	import Elixys.Extended.Form;
	import Elixys.Extended.Input;
	import Elixys.Interfaces.ITextBox;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Components.ComponentCassette;
	import Elixys.JSON.Components.Components;
	import Elixys.JSON.Post.PostSequence;
	import Elixys.JSON.State.Reagent;
	import Elixys.JSON.State.RunState;
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
										sComponentType:String, pRunXML:XML, attributes:Attributes)
		{
			// Call the base constructor
			super(screen, sMode, pElixys, sComponentType, nButtonWidth, VIEW_UNITOPERATION, 
				EDIT_UNITOPERATION, pRunXML, attributes);

			// Initialize depending on the mode
			switch (m_sMode)
			{
				case Constants.VIEW:
				case Constants.EDIT:
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
								m_pFieldContents.push(CreateDropdownControl());
								break;
							
							case Constants.TYPE_INPUT:
								m_pFieldContents.push(CreateInputControl());
								break;
							
							case Constants.TYPE_MULTILINEINPUT:
								m_pFieldContents.push(CreateMultilineInputControl());
								break;
							
							case Constants.TYPE_CHECKBOX:
								m_pFieldContents.push(CreateCheckboxControl());
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
					break;
				
				case Constants.RUN:
					// This object is the container
					m_pUnitOperationContainer = this;
					
					// Get the class and set the field count to zero
					m_pComponentClass = Components.GetComponentClass(sComponentType);
					m_nComponentFieldCount = 0;
					break;
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

		// Updates the run state
		public override function UpdateRunState(pRunState:RunState):void
		{
			// Call the base implemetation and update
			super.UpdateRunState(pRunState);
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
			
			// Update the unit operation number and name in view and edit modes
			if ((m_sMode == Constants.VIEW) || (m_sMode == Constants.EDIT))
			{
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
			}
			
			// Iterate over each field
			for (nIndex = 0; nIndex < m_nComponentFieldCount; ++nIndex)
			{
				// Set the field contents
				switch (m_pComponentFieldTypes[nIndex])
				{
					case Constants.TYPE_DROPDOWN:
						SetDropdownControl(m_pFieldContents[nIndex], m_pComponent[m_pComponentFieldProperties[nIndex]]);
						break;
					
					case Constants.TYPE_INPUT:
						SetInputControl(m_pFieldContents[nIndex], m_pComponent[m_pComponentFieldProperties[nIndex]]);
						break;

					case Constants.TYPE_MULTILINEINPUT:
						SetMultilineInputControl(m_pFieldContents[nIndex], m_pComponent[m_pComponentFieldProperties[nIndex]]);
						break;

					case Constants.TYPE_CHECKBOX:
						SetCheckboxControl(m_pFieldContents[nIndex], m_pComponent[m_pComponentFieldProperties[nIndex]]);
						break;
				}
			
				// Set the error text
				(m_pFieldErrors[nIndex] as UILabel).text = m_pComponent[m_pComponentFieldProperties[nIndex] + "Error"];
			}
			
			// Adjust the layout
			AdjustPositions();
		}

		// Adjusts the view component positions
		protected function AdjustPositions():void
		{
			// Adjust the unit operation number and background skin in view and edit modes
			if ((m_sMode == Constants.VIEW) || (m_sMode == Constants.EDIT))
			{
				m_pUnitOperationNumber.width = m_pUnitOperationNumber.textWidth + 8;
				var pSubviewPoint:Point = globalToLocal(m_pUnitOperationNumber.localToGlobal(
					new Point(m_pUnitOperationNumber.x, m_pUnitOperationNumber.y)));
				m_pUnitOperationNumberBackground.width = m_pUnitOperationNumber.width + 
					(2 * UNITOPERATIONHEADERPADDING);
				m_pUnitOperationNumberBackground.height = m_pUnitOperationNumber.height + 
					(2 * UNITOPERATIONHEADERPADDING);
				m_pUnitOperationNumberBackground.x = pSubviewPoint.x - UNITOPERATIONHEADERPADDING;
				m_pUnitOperationNumberBackground.y = pSubviewPoint.y - UNITOPERATIONHEADERPADDING;
			}
			
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
						AdjustDropdownControl(m_pFieldContents[nIndex], nContentWidth, nRowHeight, nOffsetX, nOffsetY);
						break;
					
					case Constants.TYPE_INPUT:
						AdjustInputControl(m_pFieldContents[nIndex], nContentWidth, nRowHeight, nOffsetX, nOffsetY);
						break;

					case Constants.TYPE_MULTILINEINPUT:
						nActualHeight = AdjustMultilineInputControl(m_pFieldContents[nIndex], nContentWidth + 
							HORIZONTALGAP + nUnitWidth + HORIZONTALGAP + nErrorWidth, nRowHeight, nOffsetX, nOffsetY);
						break;

					case Constants.TYPE_CHECKBOX:
						AdjustCheckboxControl(m_pFieldContents[nIndex], nContentWidth, nRowHeight, nOffsetX, nOffsetY);
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
			if ((m_sMode == Constants.VIEW) || (m_sMode == Constants.EDIT))
			{
				m_nInputAreaOfInterestTop = m_pUnitOperationNumber.getBounds(stage).top;
			}
			else
			{
				m_nInputAreaOfInterestTop = m_pUnitOperationContainer.getBounds(stage).top;
			}
			m_nInputAreaOfInterestBottom = m_pUnitOperationContainer.getBounds(stage).bottom;
		}

		// Creates a dropdown field
		protected function CreateDropdownControl():*
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
		protected function SetDropdownControl(pDropdown:*, pContents:*):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = pDropdown as UILabel;
					if (pContents is Reagent)
					{
						pLabel.text = (pContents as Reagent).Name;
					}
					else
					{
						pLabel.text = pContents.toString();
					}
					break;
				
				case Constants.EDIT:
					break;
			}
		}
		
		// Adust the dropdown field position
		protected function AdjustDropdownControl(pDropdown:*, nWidth:Number, nRowHeight:Number, nX:Number, nY:Number):void
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
					var pInput:Input = AddInput(22, Styling.TEXT_BLACK, Constants.RETURNKEYLABEL_NEXT);
					ConfigureTextBox(pInput.inputField);
					return pInput;

				default:
					return null;
			}
		}

		// Sets the input field contents
		protected function SetInputControl(pInput:*, pContents:*):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					(pInput as UILabel).text = pContents.toString();
					break;
					
				case Constants.EDIT:
					var pInputVar:Input = pInput as Input;
					if (pInputVar.inputField != m_pKeyboardFocusTextBox)
					{
						pInputVar.text = pContents.toString();
					}
					break;
			}
		}

		// Adust the input field position
		protected function AdjustInputControl(pInput:*, nWidth:Number, nRowHeight:Number, nX:Number, nY:Number):void
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
		protected function CreateMultilineInputControl():*
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					return AddLabel("GothamBold", 18, TextFormatAlign.LEFT);
					
				case Constants.EDIT:
					var pInput:Input = AddMultilineInput(22, Styling.TEXT_BLACK, Constants.RETURNKEYLABEL_NEXT,
						MULTILINE_HEIGHT);
					ConfigureTextBox(pInput.inputField);
					return pInput;

				default:
					return null;
			}
		}
		
		// Sets the multiline input field contents
		protected function SetMultilineInputControl(pInput:*, pContents:*):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					(pInput as UILabel).text = pContents.toString();
					break;
				
				case Constants.EDIT:
					var pInputVar:Input = pInput as Input;
					if (pInputVar.inputField != m_pKeyboardFocusTextBox)
					{
						pInputVar.text = pContents.toString();
					}
					break;
			}
		}
		
		// Adust the multiline input field position
		protected function AdjustMultilineInputControl(pInput:*, nWidth:Number, nRowHeight:Number, nX:Number, nY:Number):Number
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
					var pInputVar:Input = pInput as Input;
					var nHeight:Number = (pInputVar.inputField as ITextBox).height;
					pInputVar.FixWidth = nWidth;
					pInputVar.FixHeight = nHeight;
					pInputVar.FixX = nX;
					if (nHeight < nRowHeight)
					{
						pInputVar.FixY = nY + ((nRowHeight - nHeight) / 2);
						return nRowHeight;
					}
					else
					{
						pInputVar.FixY = nY;
						return nHeight;
					}
					
				default:
					return 0;
			}
		}
		
		// Creates a checkbox field
		protected function CreateCheckboxControl():*
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					return AddLabel("GothamBold", 18, TextFormatAlign.LEFT);

				case Constants.EDIT:
					var pCheckBox:CheckBox = AddCheckBox();
					ConfigureCheckBox(pCheckBox);
					return pCheckBox;

				default:
					return null;
			}
		}

		// Sets the checkbox field contents
		protected function SetCheckboxControl(pCheckbox:*, pContents:*):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					(pCheckbox as UILabel).text = pContents ? "YES" : "NO";
					break;
				
				case Constants.EDIT:
					(pCheckbox as CheckBox).Checked = Boolean(pContents);
					break;
			}
		}
		
		// Adust the checkbox field position
		protected function AdjustCheckboxControl(pCheckbox:*, nWidth:Number, nRowHeight:Number, nX:Number, nY:Number):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = pCheckbox as UILabel;
					pLabel.x = nX + (nWidth - pLabel.width);
					pLabel.y = nY + ((nRowHeight - pLabel.height) / 2);
					break;
				
				case Constants.EDIT:
					var pCheckboxVar:CheckBox = pCheckbox as CheckBox;
					pCheckboxVar.x = nX;
					pCheckboxVar.y = nY;
					pCheckboxVar.width = nWidth;
					pCheckboxVar.height = nRowHeight;
					break;
			}
		}

		// Called when the user changes the text in one of our input fields
		protected override function OnTextValueChanged(pFocusTarget:ITextBox):void
		{
			// Only handle when in edit mode
			if (m_sMode == Constants.EDIT)
			{
				// Locate and the field that the user was editing
				var nIndex:int, pInput:Input;
				for (nIndex = 0; nIndex < m_nComponentFieldCount; ++nIndex)
				{
					if ((m_pComponentFieldTypes[nIndex] == Constants.TYPE_INPUT) || 
						(m_pComponentFieldTypes[nIndex] == Constants.TYPE_MULTILINEINPUT))
					{
						pInput = m_pFieldContents[nIndex] as Input;
						if (pInput.inputField == pFocusTarget)
						{
							// Set the component field and the reset the input text since the 
							// component may have altered the value
							m_pComponent[m_pComponentFieldProperties[nIndex]] = pInput.text;
							pInput.text = m_pComponent[m_pComponentFieldProperties[nIndex]];
							break;
						}
					}
				}

				// Post the component to the server
				PostComponent(m_pComponent);
			}
		}

		// Called when the user changes the state of a check box
		protected override function OnCheckBoxChanged(event:CheckBoxEvent):void
		{
			// Only handle when in edit mode
			if (m_sMode == Constants.EDIT)
			{
				// Locate and the check box that has changed
				var nIndex:int, pCheckBox:CheckBox;
				for (nIndex = 0; nIndex < m_nComponentFieldCount; ++nIndex)
				{
					if (m_pComponentFieldTypes[nIndex] == Constants.TYPE_CHECKBOX)
					{
						pCheckBox = m_pFieldContents[nIndex] as CheckBox;
						if (pCheckBox == event.checkbox)
						{
							// Set the component field
							m_pComponent[m_pComponentFieldProperties[nIndex]] = pCheckBox.Checked;
							break;
						}
					}
				}
				
				// Post the component to the server
				PostComponent(m_pComponent);
			}
		}

		// Called when a button on the unit operation is clicked
		protected function OnButtonClick(event:ButtonEvent):void
		{
			// Send a button click to the server
			var pPostSequence:PostSequence = new PostSequence();
			pPostSequence.TargetID = event.button;
			DoPost(pPostSequence, m_sMode);
		}

		/***
		 * Member variables
		 **/

		// Subview view XML
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
					<frame id="unitoperationcontainer" background={Styling.APPLICATION_BACKGROUND} />
				</rows>
			</columns>;

		// Subview edit XML
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
					<frame id="unitoperationcontainer" background={Styling.APPLICATION_BACKGROUND} />
				</rows>
			</columns>;
		
		// Subview run XMLs
		protected static const RUN_UNITOPERATION_BLANK:XML = 
			<frame id="unitoperationcontainer" background={Styling.APPLICATION_BACKGROUND} />;
		protected static const RUN_UNITOPERATION_ONEVIDEO:XML = 
			<frame id="unitoperationcontainer" background="#FFFF00" />;
		
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
		public static const UNITOPERATIONHEADERPADDING:int = 5;
		protected static const HORIZONTALGAP:int = 10;
		protected static const LABELPERCENTWIDTH:int = 30;
		protected static const CONTENTSPERCENTWIDTH:int = 25;
		protected static const UNITSPERCENTWIDTH:int = 20;
		protected static const ERRORSPERCENTWIDTH:int = 25;
		protected static const ROWPERCENTHEIGHT:int = 15;
		protected static const MULTILINE_HEIGHT:int = 5;
	}
}
