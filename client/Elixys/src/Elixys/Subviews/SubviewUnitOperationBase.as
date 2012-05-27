package Elixys.Subviews
{
	import Elixys.Assets.Constants;
	import Elixys.Assets.Styling;
	import Elixys.Components.Button;
	import Elixys.Components.CheckBox;
	import Elixys.Components.Utils;
	import Elixys.Events.ButtonEvent;
	import Elixys.Events.CheckBoxEvent;
	import Elixys.Events.DropdownEvent;
	import Elixys.Events.ScrollClickEvent;
	import Elixys.Extended.Form;
	import Elixys.Extended.Input;
	import Elixys.Extended.ScrollVertical;
	import Elixys.Interfaces.ITextBox;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Components.ComponentCassette;
	import Elixys.JSON.Components.Components;
	import Elixys.JSON.Post.PostSequence;
	import Elixys.JSON.State.Reagent;
	import Elixys.JSON.State.Reagents;
	import Elixys.JSON.State.RunState;
	import Elixys.JSON.State.Sequence;
	import Elixys.JSON.State.SequenceComponent;
	import Elixys.Views.SequenceEdit;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObjectContainer;
	import flash.display.GradientType;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.geom.Matrix;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextFormatAlign;
	
	import mx.utils.StringUtil;

	// This unit operation base class is an extension of the subview base class
	public class SubviewUnitOperationBase extends SubviewBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewUnitOperationBase(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
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
					m_pUnitOperationNumberBackground = Utils.AddSkin(sequencer_titleBar_mc, true, this, 0, 0, 0);
					
					// Add the fade fields
					m_pUnitOperationFadeTop = new Sprite();
					m_pUnitOperationFadeTop.mouseEnabled = false;
					m_pUnitOperationFadeTop.visible = false;
					m_pUnitOperationContainer.parent.addChild(m_pUnitOperationFadeTop);
					m_pUnitOperationFadeBottom = new Sprite();
					m_pUnitOperationFadeBottom.mouseEnabled = false;
					m_pUnitOperationFadeBottom.visible = false;
					m_pUnitOperationContainer.parent.addChild(m_pUnitOperationFadeBottom);

					// Add the horizontal scroller
					var pAttributes:Attributes = new Attributes(0, 0, m_pUnitOperationContainer.attributes.width, 
						m_pUnitOperationContainer.attributes.height);
					m_pUnitOperationScroll = new ScrollVertical(m_pUnitOperationContainer, UNITOPERATION_SCROLL, pAttributes, false);
					m_pUnitOperationScroll.addEventListener(ScrollVertical.SLIDER_MOVED, OnSliderMove);
					m_pUnitOperationScroll.addEventListener(ScrollClickEvent.CLICK, OnScrollClick);
					m_pUnitOperationSlider = m_pUnitOperationScroll.pages[0] as Form;

					// Get references to the component fields
					m_pComponentClass = Components.GetComponentClass(sComponentType);
					m_nComponentFieldCount = m_pComponentClass.FIELDCOUNT;
					m_pComponentFieldLabels = m_pComponentClass.FIELDLABELS;
					m_pComponentFieldTypes = m_pComponentClass.FIELDTYPES;
					m_pComponentFieldUnits = m_pComponentClass.FIELDUNITS;
					m_pComponentFieldProperties = m_pComponentClass.FIELDPROPERTIES;
					
					// Initialize the fields
					var nIndex:int, pLabel:UILabel, pArrow:Sprite, pHitArea:Rectangle;
					for (nIndex = 0; nIndex < m_nComponentFieldCount; ++nIndex)
					{
						// Create label
						pLabel = Utils.AddLabel("", this, "GothamBold", 18, Styling.AS3Color(Styling.TEXT_BLACK),
							m_pUnitOperationSlider);
						pLabel.text = m_pComponentFieldLabels[nIndex];
						m_pFieldLabels.push(pLabel);
						
						// Create contents
						pArrow = null;
						pHitArea = null;
						switch (m_pComponentFieldTypes[nIndex])
						{
							case Constants.TYPE_DROPDOWN:
								m_pFieldContents.push(CreateDropdownControl());
								if (m_sMode == Constants.EDIT)
								{
									pArrow = Utils.AddSkin(slidingList_arrow_up, true, m_pUnitOperationSlider);
								}
								pHitArea = new Rectangle();
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
						m_pFieldArrows.push(pArrow);
						m_pFieldHitAreas.push(pHitArea);
						
						// Create units label
						pLabel = Utils.AddLabel("", this, "GothamBold", 18, Styling.AS3Color(Styling.TEXT_BLACK),
							m_pUnitOperationSlider);
						pLabel.text = m_pComponentFieldUnits[nIndex];
						pLabel.textColor = Styling.AS3Color(Styling.TEXT_GRAY4);
						m_pFieldUnits.push(pLabel);
						
						// Create blank entry in error field array
						m_pFieldErrors.push(null);
					}
					
					if (m_sMode == Constants.EDIT)
					{
						// Find the parent edit sequence
						var pParent:DisplayObjectContainer = screen;
						while ((pParent != null) && !(pParent is SequenceEdit))
						{
							pParent = pParent.parent;
						}
						if (pParent is SequenceEdit)
						{
							m_pSequenceEdit = pParent as SequenceEdit;
						}
						
						// Add event listeners
						addEventListener(DropdownEvent.ITEMSELECTED, OnDropdownItemSelected);
						addEventListener(DropdownEvent.LISTHIDDEN, OnDropdownListHidden);
					}
					break;
				
				case Constants.RUN:
					// This object is the container
					m_pUnitOperationContainer = this;
					
					// Remember the component class
					m_pComponentClass = Components.GetComponentClass(sComponentType);
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
			// Hide the dropdown list if the component ID has changed
			if (m_pComponent && (pComponent.ID != m_pComponent.ID))
			{
				HideDropdownList();
			}
			
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

		// Updates the reagent list
		public override function UpdateReagents(pReagents:Reagents):void
		{
			// Show the dropdown control if we are waiting on a reagent list
			if (m_sDropdownIndex != -1)
			{
				var pReagent:Reagent;
				for (var i:int = 0; i < pReagents.ReagentList.length; ++i)
				{
					pReagent = pReagents.ReagentList[i] as Reagent;
					m_pDropdownValues.push(pReagent.Name);
					m_pDropdownData.push(pReagent);
				}
				ShowDropdownList();
			}
		}

		// Updates the subview
		protected function Update():void
		{
			if ((m_sMode == Constants.VIEW) || (m_sMode == Constants.EDIT))
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
			
				// Adjust the height of the slider
				var nSliderHeight:Number = CalculateSliderHeight();
				if (m_pUnitOperationSlider.attributes.height != nSliderHeight)
				{
					if (nSliderHeight < m_pUnitOperationScroll.attributes.height)
					{
						m_pUnitOperationSlider.ForceHeight(m_pUnitOperationScroll.attributes.height);
						m_pUnitOperationScroll.scrollEnabled = false;
						m_pUnitOperationScroll.doLayout();
						m_pUnitOperationFadeTop.visible = false;
						m_pUnitOperationFadeBottom.visible = false;
					}
					else
					{
						m_pUnitOperationSlider.ForceHeight(nSliderHeight);
						m_pUnitOperationScroll.scrollEnabled = true;
						m_pUnitOperationScroll.doLayout();
						UpdateFadeVisibility();
					}
				}
				
				// Iterate over each field
				var sError:String, pLabel:UILabel;
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
				
					// Set the error field
					sError = m_pComponent[m_pComponentFieldProperties[nIndex] + "Error"];
					if (sError != "")
					{
						if (!m_pFieldErrors[nIndex])
						{
							pLabel = Utils.AddLabel("", this, "GothamBold", 18, Styling.AS3Color(Styling.TEXT_BLACK),
								m_pUnitOperationSlider);
							pLabel.textColor = Styling.AS3Color(Styling.TEXT_RED);
							m_pFieldErrors[nIndex] = pLabel;
						}
						(m_pFieldErrors[nIndex] as UILabel).text = sError;
					}
					else if (m_pFieldErrors[nIndex])
					{
						m_pUnitOperationSlider.removeChild(m_pFieldErrors[nIndex]);
						m_pFieldErrors[nIndex] = null;
					}
				}
			}
			
			// Adjust the layout
			AdjustPositions();
		}

		// Calculates the required height of the slider
		protected function CalculateSliderHeight():Number
		{
			// Sum the height of the components
			var nHeight:Number = SCROLL_VERTICAL_PADDING * 2;
			var nIndex:int, nComponentHeight:Number;
			for (nIndex = 0; nIndex < m_nComponentFieldCount; ++nIndex)
			{
				nHeight += CalculateRowHeight(nIndex);
			}
			return nHeight;
		}
		
		// Calculates the required height of the field
		protected function CalculateRowHeight(nIndex:int):Number
		{
			// Add the height of the component
			var nComponentHeight:Number;
			switch (m_pComponentFieldTypes[nIndex])
			{
				case Constants.TYPE_DROPDOWN:
					nComponentHeight = GetDropdownControlHeight(m_pFieldContents[nIndex]);
					break;
				
				case Constants.TYPE_INPUT:
					nComponentHeight = GetInputControlHeight(m_pFieldContents[nIndex]);
					break;
				
				case Constants.TYPE_MULTILINEINPUT:
					nComponentHeight = GetMultilineInputControlHeight(m_pFieldContents[nIndex]);
					break;
				
				case Constants.TYPE_CHECKBOX:
					nComponentHeight = GetCheckboxControlHeight(m_pFieldContents[nIndex]);
					break;
			}
			var nTotalHeight:Number = 0;
			if ((nComponentHeight + (2 * ROWVERTICALPADDING)) < ROWCONTENTHEIGHT)
			{
				nTotalHeight += ROWCONTENTHEIGHT;
			}
			else
			{
				nTotalHeight += nComponentHeight + (2 * ROWVERTICALPADDING);
			}
			
			// Add space for any error message
			if (m_pComponent)
			{
				if (m_pComponent[m_pComponentFieldProperties[nIndex] + "Error"] != "")
				{
					nTotalHeight += ROWERRORHEIGHT;
				}
			}
			return nTotalHeight;
		}
		
		// Called when the slider moves
		protected function OnSliderMove(event:Event):void
		{
			UpdateFadeVisibility();
		}
		
		// Updates the visibility of the fade layers
		protected function UpdateFadeVisibility():void
		{
			m_pUnitOperationFadeTop.visible = (m_pUnitOperationScroll.scrollPositionY > FADE_THRESHOLD);
			m_pUnitOperationFadeBottom.visible = 
				((m_pUnitOperationScroll.scrollPositionY + FADE_THRESHOLD) < m_pUnitOperationScroll.MaximumSlide);
		}
		
		// Called when the scroll area is clicked
		protected function OnScrollClick(event:ScrollClickEvent):void
		{
			// Hit test
			var nIndex:int, pHitArea:Rectangle, pReagent:Reagent;
			for (nIndex = 0; nIndex < m_pFieldHitAreas.length; ++nIndex)
			{
				if (m_pFieldHitAreas[nIndex])
				{
					pHitArea = m_pFieldHitAreas[nIndex] as Rectangle;
					if (pHitArea.contains(event.x, event.y))
					{
						// Found it.  Get the current value of this field and the list of acceptable values from the 
						// validation string
						if (m_pComponent[m_pComponentFieldProperties[nIndex]] is Reagent)
						{
							pReagent = m_pComponent[m_pComponentFieldProperties[nIndex]] as Reagent;
							if (pReagent.Name)
							{
								m_sDropdownCurrentValue = pReagent.Name;
							}
							else
							{
								m_sDropdownCurrentValue = "";
							}
						}
						else
						{
							m_sDropdownCurrentValue = m_pComponent[m_pComponentFieldProperties[nIndex]].toString();
						}
						var sValidation:String = m_pComponent[m_pComponentFieldProperties[nIndex] + "Validation"];

						// Create an array of key-value pairs from the validation string
						var pFields:Array = sValidation.split(";");
						var pFieldValidation:Object = new Object(), sField:String, pKeyValue:Array;
						for each (sField in pFields)
						{
							pKeyValue = sField.split("=");
							pFieldValidation[StringUtil.trim(pKeyValue[0])] = StringUtil.trim(pKeyValue[1]);
						}

						// Remember the dropdown parameters
						m_sDropdownIndex = nIndex;
						m_sDropdownType = pFieldValidation["type"];
						m_pDropdownValues = new Array();
						m_pDropdownData = new Array();
						m_sDropdownErrorMessage = "";

						// What type of list do we have?
						var pValues:Array = pFieldValidation["values"].split(",");
						if ((m_sDropdownType == "enum-number") || (m_sDropdownType == "enum-string"))
						{
							// We already have the values to display
							for (var i:int = 0; i < pValues.length; ++i)
							{
								m_pDropdownValues.push(pValues[i].toString());
							}
							ShowDropdownList();
						}
						else
						{
							// Check if we have a list of one or more reagents
							if ((pValues.length > 0) && (pValues[0] != ""))
							{
								// Load the reagents from the server
								GetReagents(pValues);
							}
							else
							{
								// Show the dropdown list with a help message
								m_sDropdownErrorMessage = "There are no unused reagents to choose from.  Use the Cassettes tab to the left to add new reagents.";
								ShowDropdownList();
							}
						}
						return;
					}
				}
			}
		}
		
		// Adjusts the view component positions
		protected function AdjustPositions():void
		{
			if ((m_sMode == Constants.VIEW) || (m_sMode == Constants.EDIT))
			{
				// Adjust the unit operation number and background skin
				var pParent:Form = m_pUnitOperationNumber.parent as Form;
				m_pUnitOperationNumber.width = m_pUnitOperationNumber.textWidth + 8;
				m_pUnitOperationNumber.x = 0;
				m_pUnitOperationNumber.y = (pParent.attributes.height - m_pUnitOperationNumber.height) / 2;
				var pSubviewPoint:Point = globalToLocal(pParent.localToGlobal(
					new Point(m_pUnitOperationNumber.x, m_pUnitOperationNumber.y)));
				m_pUnitOperationNumberBackground.width = m_pUnitOperationNumber.width + 
					(2 * UNITOPERATIONHEADERPADDING);
				m_pUnitOperationNumberBackground.height = m_pUnitOperationNumber.height + 
					(2 * UNITOPERATIONHEADERPADDING);
				m_pUnitOperationNumberBackground.x = pSubviewPoint.x - UNITOPERATIONHEADERPADDING;
				m_pUnitOperationNumberBackground.y = pSubviewPoint.y - UNITOPERATIONHEADERPADDING;
				
				// Adjust the unit operation name
				pParent = m_pUnitOperationName.parent as Form;
				m_pUnitOperationName.width = pParent.attributes.width;
				m_pUnitOperationName.x = 0;
				m_pUnitOperationName.y = (pParent.attributes.height - m_pUnitOperationName.height) / 2;

				// Draw the fade gradients
				var nFadeHeight:Number = m_pUnitOperationContainer.attributes.height * FADE_HEIGHT / 100;
				var pColors:Array = [0xFFFFFF, 0xFFFFFF];
				var pAlphas:Array = [0.9, 0];
				var pRatios:Array = [0, 255];
				var pTopMatrix:Matrix = new Matrix();
				pTopMatrix.createGradientBox(m_pUnitOperationContainer.attributes.width, nFadeHeight, Math.PI / 2, 
					m_pUnitOperationContainer.x, m_pUnitOperationContainer.y);
				m_pUnitOperationFadeTop.graphics.clear();
				m_pUnitOperationFadeTop.graphics.lineStyle();
				m_pUnitOperationFadeTop.graphics.beginGradientFill(GradientType.LINEAR, pColors, pAlphas, pRatios, pTopMatrix);
				m_pUnitOperationFadeTop.graphics.drawRect(m_pUnitOperationContainer.x, m_pUnitOperationContainer.y,
					m_pUnitOperationContainer.attributes.width, nFadeHeight);
				m_pUnitOperationFadeTop.graphics.endFill();
				var pBottomMatrix:Matrix = new Matrix();
				var nOffsetY:Number = m_pUnitOperationContainer.y + m_pUnitOperationContainer.attributes.height - nFadeHeight;
				pBottomMatrix.createGradientBox(m_pUnitOperationContainer.attributes.width, nFadeHeight, -Math.PI / 2,
					m_pUnitOperationContainer.x, nOffsetY);
				m_pUnitOperationFadeBottom.graphics.clear();
				m_pUnitOperationFadeBottom.graphics.beginGradientFill(GradientType.LINEAR, pColors, pAlphas, pRatios, pBottomMatrix);
				m_pUnitOperationFadeBottom.graphics.drawRect(m_pUnitOperationContainer.x, nOffsetY, 
					m_pUnitOperationContainer.attributes.width, nFadeHeight + 1);
				m_pUnitOperationFadeBottom.graphics.endFill();
			
				// Draw the dividers and set the field positions
				var nIndex:int, pLabel:UILabel, pUnits:UILabel, pArrow:Sprite, pError:UILabel, pHitArea:Rectangle, 
					nRowHeight:Number, nFieldRight:Number, nFieldWidth:Number;
				nOffsetY = SCROLL_VERTICAL_PADDING;
				m_pUnitOperationSlider.graphics.clear();
				m_pUnitOperationSlider.graphics.beginFill(Styling.AS3Color(Styling.UNITOPERATION_DIVIDER));
				for (nIndex = 0; nIndex < m_nComponentFieldCount; ++nIndex)
				{
					// Calculate the row height
					nRowHeight = CalculateRowHeight(nIndex);
					
					// Draw the top divider
					m_pUnitOperationSlider.graphics.drawRect(0, nOffsetY - (DIVIDER_HEIGHT / 2), m_pUnitOperationSlider.attributes.width, DIVIDER_HEIGHT);

					// Skip this field if the label is not visible
					pLabel = m_pFieldLabels[nIndex] as UILabel;
					if (!pLabel.visible)
					{
						continue;
					}

					// Adjust the label
					pLabel.x = HORIZONTALGAP;
					pLabel.y = nOffsetY + ((ROWCONTENTHEIGHT - pLabel.textHeight) / 2);

					// Adjust the units label
					pUnits = m_pFieldUnits[nIndex] as UILabel;
					pUnits.x = m_pUnitOperationSlider.attributes.width - RIGHTGAP - pUnits.textWidth;
					if (m_sMode == Constants.EDIT)
					{
						pUnits.x -= ROWARROWWIDTH + HORIZONTALGAP;
					}
					pUnits.y = nOffsetY + ((ROWCONTENTHEIGHT - pUnits.textHeight) / 2);

					// Adjust the contents
					nFieldRight = pLabel.x + pLabel.width + HORIZONTALGAP;
					nFieldWidth = pUnits.x - nFieldRight;
					if (pUnits.text != "")
					{
						nFieldWidth -= HORIZONTALGAP;
					}
					switch (m_pComponentFieldTypes[nIndex])
					{
						case Constants.TYPE_DROPDOWN:
							AdjustDropdownControl(m_pFieldContents[nIndex], nFieldRight, nOffsetY, nFieldWidth, ROWCONTENTHEIGHT);
							break;
						
						case Constants.TYPE_INPUT:
							AdjustInputControl(m_pFieldContents[nIndex], nFieldRight, nOffsetY, nFieldWidth, ROWCONTENTHEIGHT);
							break;
	
						case Constants.TYPE_MULTILINEINPUT:
							var nMultilineHeight:Number = nRowHeight;
							if (m_pComponent && (m_pComponent[m_pComponentFieldProperties[nIndex] + "Error"] != ""))
							{
								nMultilineHeight -= ROWERRORHEIGHT + ROWVERTICALPADDING;
							}
							AdjustMultilineInputControl(m_pFieldContents[nIndex], nFieldRight, nOffsetY, nFieldWidth, nMultilineHeight);
							break;
	
						case Constants.TYPE_CHECKBOX:
							AdjustCheckboxControl(m_pFieldContents[nIndex], nFieldRight, nOffsetY + (ROWVERTICALPADDING / 2), 
								nFieldWidth, nRowHeight - ROWVERTICALPADDING);
							break;
					}

					// Adjust the arrow
					if (m_pFieldArrows[nIndex])
					{
						pArrow = m_pFieldArrows[nIndex] as Sprite;
						pArrow.x = m_pUnitOperationSlider.attributes.width - RIGHTGAP - pArrow.width;
						pArrow.y = nOffsetY + ((ROWCONTENTHEIGHT - pArrow.height) / 2);
					}
					
					// Set the hit area
					if (m_pFieldHitAreas[nIndex])
					{
						pHitArea = m_pFieldHitAreas[nIndex] as Rectangle;
						pHitArea.x = 0;
						pHitArea.y = nOffsetY;
						pHitArea.width =  m_pUnitOperationSlider.attributes.width;
						pHitArea.height = nRowHeight;
					}

					// Adjust the error label
					if (m_pFieldErrors[nIndex])
					{
						pError = m_pFieldErrors[nIndex] as UILabel;
						pError.x = m_pUnitOperationSlider.attributes.width - RIGHTGAP - pError.textWidth;
						if (m_sMode == Constants.EDIT)
						{
							pError.x -= ROWARROWWIDTH + HORIZONTALGAP;
						}
						pError.y = nOffsetY + nRowHeight - ROWERRORHEIGHT - (ROWVERTICALPADDING * 2);
					}
					
					// Adjust the offset
					nOffsetY += nRowHeight;
				}
				
				// Draw the bottom divider
				m_pUnitOperationSlider.graphics.drawRect(0, nOffsetY - (DIVIDER_HEIGHT / 2), m_pUnitOperationSlider.attributes.width, DIVIDER_HEIGHT);
				m_pUnitOperationSlider.graphics.endFill();
	
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
		}

		// Creates a dropdown field
		protected function CreateDropdownControl():*
		{
			var pLabel:UILabel;
			switch (m_sMode)
			{
				case Constants.VIEW:
					pLabel = Utils.AddLabel("", this, "GothamBold", 18, Styling.AS3Color(Styling.TEXT_BLACK),
						m_pUnitOperationSlider);
					pLabel.textColor = Styling.AS3Color(Styling.TEXT_BLUE4);
					return pLabel;
					
				case Constants.EDIT:
					pLabel = Utils.AddLabel("", this, "GothamBold", 18, Styling.AS3Color(Styling.TEXT_BLACK),
						m_pUnitOperationSlider);
					pLabel.textColor = Styling.AS3Color(Styling.TEXT_BLUE4);
					return pLabel;

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
				case Constants.EDIT:
					var pLabel:UILabel = pDropdown as UILabel;
					if (pContents is Reagent)
					{
						var pReagent:Reagent = pContents as Reagent;
						if (pReagent.Name)
						{
							pLabel.text = (pContents as Reagent).Name;
						}
						else
						{
							pLabel.text = "";
						}
					}
					else
					{
						pLabel.text = pContents.toString();
					}
					break;
			}
		}
		
		// Gets the height of the dropdown field
		protected function GetDropdownControlHeight(pDropdown:*):Number
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
				case Constants.EDIT:
					var pLabel:UILabel = pDropdown as UILabel;
					return pLabel.height;
			}
			return 0;
		}
		
		// Adust the dropdown field position
		protected function AdjustDropdownControl(pDropdown:*, nX:Number, nY:Number, nWidth:Number, nHeight:Number):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
				case Constants.EDIT:
					var pLabel:UILabel = pDropdown as UILabel;
					pLabel.x = nX + nWidth - pLabel.textWidth;
					pLabel.y = nY + ((nHeight - pLabel.textHeight) / 2);
					break;
			}
		}

		// Creates an input field
		protected function CreateInputControl():*
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = Utils.AddLabel("", this, "GothamBold", 18, 
						Styling.AS3Color(Styling.TEXT_BLACK), m_pUnitOperationSlider);
					pLabel.textColor = Styling.AS3Color(Styling.TEXT_BLUE4);
					return pLabel;
					
				case Constants.EDIT:
					var pInput:Input = AddSkinlessInput(22, Styling.TEXT_BLUE4, Constants.RETURNKEYLABEL_NEXT, m_pUnitOperationSlider);
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

		// Gets the input field height
		protected function GetInputControlHeight(pInput:*):Number
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					return (pInput as UILabel).height;
					
				case Constants.EDIT:
					return (pInput as Input).inputField.height;
			}
			return 0;
		}
		
		// Adust the input field position
		protected function AdjustInputControl(pInput:*, nX:Number, nY:Number, nWidth:Number, nHeight:Number):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = pInput as UILabel;
					pLabel.x = nX + nWidth - pLabel.textWidth;
					pLabel.y = nY + ((nHeight - pLabel.textHeight) / 2);
					break;

				case Constants.EDIT:
					var pInputVar:Input = pInput as Input;
					pInputVar.FixWidth = nWidth;
					pInputVar.FixHeight = pInputVar.inputField.height;
					pInputVar.FixX = nX;
					pInputVar.FixY = nY + ((nHeight - pInputVar.height) / 2);
					break;
			}
		}

		// Creates an multiline input field
		protected function CreateMultilineInputControl():*
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = Utils.AddLabel("", this, "GothamBold", 18, 
						Styling.AS3Color(Styling.TEXT_BLACK), m_pUnitOperationSlider);
					pLabel.textColor = Styling.AS3Color(Styling.TEXT_BLUE4);
					return pLabel;
					
				case Constants.EDIT:
					var pInput:Input = AddSkinlessMultilineInput(22, Styling.TEXT_BLUE4, MULTILINE_HEIGHT, m_pUnitOperationSlider);
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
		
		// Gets the multiline input field height
		protected function GetMultilineInputControlHeight(pInput:*):Number
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					return (pInput as UILabel).height;
					
				case Constants.EDIT:
					return (pInput as Input).inputField.height;
			}
			return 0;
		}
		
		// Adust the multiline input field position
		protected function AdjustMultilineInputControl(pInput:*, nX:Number, nY:Number, nWidth:Number, nHeight:Number):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = pInput as UILabel;
					pLabel.fixwidth = nWidth;
					if (pLabel.numLines == 1)
					{
						pLabel.x = nX + nWidth - pLabel.textWidth;
					}
					else
					{
						pLabel.x = nX;
					}
					pLabel.y = nY + (nHeight - pLabel.textHeight) / 2;
					break;
				
				case Constants.EDIT:
					var pInputVar:Input = pInput as Input;
					pInputVar.FixWidth = nWidth;
					pInputVar.FixHeight = nHeight - (3 * ROWVERTICALPADDING);
					pInputVar.FixX = nX;
					pInputVar.FixY = nY + (1.5 * ROWVERTICALPADDING);
					break;
			}
		}
		
		// Creates a checkbox field
		protected function CreateCheckboxControl():*
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					return Utils.AddLabel("", this, "GothamBold", 18, Styling.AS3Color(Styling.TEXT_BLUE4),
						m_pUnitOperationSlider);

				case Constants.EDIT:
					var pCheckBox:CheckBox = AddCheckBox(m_pUnitOperationSlider);
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

		// Gets the checkbox field height
		protected function GetCheckboxControlHeight(pCheckbox:*):Number
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					return (pCheckbox as UILabel).height;
				
				case Constants.EDIT:
					return (pCheckbox as CheckBox).height;
			}
			return 0;
		}

		// Adust the checkbox field position
		protected function AdjustCheckboxControl(pCheckbox:*, nX:Number, nY:Number, nWidth:Number, nHeight:Number):void
		{
			switch (m_sMode)
			{
				case Constants.VIEW:
					var pLabel:UILabel = pCheckbox as UILabel;
					pLabel.x = nX + nWidth - pLabel.textWidth;
					pLabel.y = nY + ((nHeight - pLabel.textHeight) / 2);
					break;
				
				case Constants.EDIT:
					var pCheckboxVar:CheckBox = pCheckbox as CheckBox;
					pCheckboxVar.x = nX;
					pCheckboxVar.y = nY;
					pCheckboxVar.width = nWidth;
					pCheckboxVar.height = ROWCONTENTHEIGHT - 5;
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
				// Locate the check box that has changed
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
			FindScreen().DoPost(pPostSequence, m_sMode);
		}

		// Shows the dropdown list
		protected function ShowDropdownList():void
		{
			m_pSequenceEdit.ShowDropdownList(m_pDropdownValues, m_sDropdownCurrentValue, m_pUnitOperationContainer, 
				this, m_pDropdownData, m_sDropdownErrorMessage);
			m_pUnitOperationScroll.visible = false;
			m_pUnitOperationFadeTop.visible = false;
			m_pUnitOperationFadeBottom.visible = false;
		}
		
		// Hides the dropdown list
		protected function HideDropdownList():void
		{
			if (m_pSequenceEdit && m_pUnitOperationScroll)
			{
				// Hide the dropdown list and show the unit operation
				m_sDropdownIndex = -1;
				m_pSequenceEdit.HideDropdownList();
				m_pUnitOperationScroll.visible = true;
				UpdateFadeVisibility();
			}
		}
		
		// Called when the user selects an item from the dropdown list
		protected function OnDropdownItemSelected(event:DropdownEvent):void
		{
			// Set the component field
			if (event.selectedData)
			{
				m_pComponent[m_pComponentFieldProperties[m_sDropdownIndex]] = event.selectedData as Reagent;
			}
			else
			{
				m_pComponent[m_pComponentFieldProperties[m_sDropdownIndex]] = event.selectedValue;
			}

			/// Hide the dropdown list
			HideDropdownList();

			// Post the component to the server
			PostComponent(m_pComponent);
		}

		// Called when the dropdown list is hidden
		protected function OnDropdownListHidden(event:DropdownEvent):void
		{
			/// Hide the dropdown list
			HideDropdownList();
		}
		
		// Overridden visiblilty setter
		public override function set visible(bVisible:Boolean):void
		{
			// Hide the dropdown if we're being hidden
			if (!bVisible)
			{
				HideDropdownList();
			}
			
			// Call the base setter
			super.visible = bVisible;
		}
		
		/***
		 * Member variables
		 **/

		// Subview view XML
		protected static const VIEW_UNITOPERATION:XML = 
			<columns gapH="0" widths="20,100%,20">
				<frame />
				<rows heights="9%,10,86%,5%" gapV="0">
					<columns widths="5%,95%" gapH="0">
						<frame>
							<label id="unitoperationnumber" useEmbedded="true">
								<font face="GothamMedium" color={Styling.TEXT_WHITE} size="14" />
							</label>
						</frame>
						<frame>
							<label id="unitoperationname" useEmbedded="true">
								<font face="GothamBold" color={Styling.TEXT_BLACK} size="14" />
							</label>
						</frame>
					</columns>
					<frame />
					<frame id="unitoperationcontainer" />
				</rows>
			</columns>;
		
		// Subview edit XML
		protected static const EDIT_UNITOPERATION:XML = 
			<columns gapH="0" widths="20,100%,20">
				<frame />
				<rows heights="9%,10,86%,5%" gapV="0">
					<columns widths="5%,95%" gapH="0">
						<frame>
							<label id="unitoperationnumber" useEmbedded="true">
								<font face="GothamMedium" color={Styling.TEXT_WHITE} size="14" />
							</label>
						</frame>
						<frame>
							<label id="unitoperationname" useEmbedded="true">
								<font face="GothamBold" color={Styling.TEXT_BLACK} size="14" />
							</label>
						</frame>
					</columns>
					<frame />
					<frame id="unitoperationcontainer" />
				</rows>
			</columns>;

		// Unit operation scroll XML
		protected static const UNITOPERATION_SCROLL:XML =
			<frame mask="true" />;
			
		// View components
		protected var m_pUnitOperationNumber:UILabel;
		protected var m_pUnitOperationNumberBackground:Sprite;
		protected var m_pUnitOperationName:UILabel;
		protected var m_pUnitOperationContainer:Form;
		protected var m_pUnitOperationFadeTop:Sprite;
		protected var m_pUnitOperationFadeBottom:Sprite;
		protected var m_pUnitOperationScroll:ScrollVertical;
		protected var m_pUnitOperationSlider:Form;

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
		protected var m_pFieldArrows:Array = new Array();
		protected var m_pFieldHitAreas:Array = new Array();
		
		// Component from server
		protected var m_pComponent:*;

		// Parent sequence edit
		protected var m_pSequenceEdit:SequenceEdit;

		// Dropdown list variables
		protected var m_sDropdownIndex:int = -1;
		protected var m_sDropdownType:String;
		protected var m_sDropdownCurrentValue:String;
		protected var m_pDropdownValues:Array;
		protected var m_pDropdownData:Array;
		protected var m_sDropdownErrorMessage:String;

		// Constants
		public static const UNITOPERATIONHEADERPADDING:int = 5;
		public static const HORIZONTALGAP:int = 10;
		protected static const RIGHTGAP:int = 20;
		public static const ROWCONTENTHEIGHT:int = 65;
		protected static const ROWERRORHEIGHT:int = 25;
		protected static const ROWTEXTGAP:int = 20;
		protected static const ROWVERTICALPADDING:int = 3;
		protected static const ROWARROWWIDTH:int = 25;
		protected static const MULTILINE_HEIGHT:int = 5;
		protected static const FADE_HEIGHT:int = 15;
		protected static const FADE_THRESHOLD:Number = 3;
		public static const SCROLL_VERTICAL_PADDING:int = 2;
		public static const DIVIDER_HEIGHT:int = 3;
	}
}
