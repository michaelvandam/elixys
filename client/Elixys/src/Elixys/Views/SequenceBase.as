package Elixys.Views
{
	import Elixys.Assets.*;
	import Elixys.Components.*;
	import Elixys.Events.*;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Post.PostSequence;
	import Elixys.JSON.State.*;
	import Elixys.Subviews.*;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.MovieClip;
	import flash.display.Sprite;
	
	// This base sequence view is an extension of the screen class
	public class SequenceBase extends Screen
	{
		/***
		 * Construction
		 **/
		
		public function SequenceBase(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, xml, attributes, row, inGroup);
			
			// Calculate the size of each unit operation button
			m_nUnitOperationWidth = attributes.width / Sequencer.VISIBLE_COLUMN_COUNT;
			m_nButtonSkinWidth = m_nUnitOperationWidth - Sequencer.BUTTON_GAP;
			
			// Get a reference to the subview
			m_pSubviewContainer = Form(findViewById("unitoperation_container"));
		}

		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public function LoadNextBase(nLoadSteps:uint):Boolean
		{
			if (m_nChildrenLoaded < nLoadSteps)
			{
				// Step 1 is loading the title bar
				if (m_pTitle == null)
				{
					LoadTitle();
				}

				// Load the subviews
				if (m_pSubviews.length < m_pSubviewTypes.length)
				{
					m_pSubviews.push(LoadSubview(m_pSubviewTypes[m_pSubviews.length]));
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
		
		// Load the navigation bar
		protected function LoadNavigationBar(sContainerID:String, pNavigationXML:XML):void
		{
			// Get the navigation bar container
			var pContainer:Form = Form(findViewById(sContainerID));
			
			// Load the navigation bar
			var pAttributes:Attributes = new Attributes(0, 0, width, height);
			m_pNavigationBar = new NavigationBar(pContainer, pNavigationXML, pAttributes);
			m_pNavigationBar.addEventListener(ButtonEvent.CLICK, OnButtonClick);
			
			// Append the navigation bar to the XML and refresh
			pContainer.xml.appendChild(pNavigationXML);
			pContainer.AppendChild(m_pNavigationBar);
			layout(attributes);
		}

		// Load the title
		protected function LoadTitle():void
		{
			// Get the title bar container
			var pContainer:Form = Form(findViewById("sequence_title_container"));
			
			// Load the title bar
			var pAttributes:Attributes = new Attributes(0, 0, pContainer.attributes.width, 
				pContainer.attributes.height);
			m_pTitle = new Form(pContainer, TITLE, pAttributes);
			
			// Append the title bar to the XML and refresh
			pContainer.xml.appendChild(TITLE);
			pContainer.AppendChild(m_pTitle);
			layout(attributes);
			
			// Add the title background and get a reference to the label
			m_pTitleBackground = new sequencer_titleBar_mc() as MovieClip;
			m_pTitle.addChildAt(m_pTitleBackground, 0);
			m_pTitleLabel = findViewById("titlelabel") as UILabel;
			
			// Update the title background position
			m_pTitleBackground.x = TITLE_PADDING;
			m_pTitleBackground.width = m_pTitle.attributes.width - (2 * TITLE_PADDING);
			m_pTitleBackground.height = m_pTitle.attributes.height;
		}

		// Load the subview
		protected function LoadSubview(pSubviewClass:Class):SubviewBase
		{
			// Load the subview
			var pAttributes:Attributes = new Attributes(0, 0, m_pSubviewContainer.attributes.width, 
				m_pSubviewContainer.attributes.height);
			return (new pSubviewClass(m_pSubviewContainer, m_sMode, m_pElixys, m_nButtonSkinWidth, 
				pAttributes)) as SubviewBase;
		}

		// Load the tab bar
		protected function LoadTabBar(sContainerID:String, pTabs:Array, sCurrentTabID:String):void
		{
			// Get the tab bar container
			var pContainer:Form = Form(findViewById(sContainerID));
			
			// Load the tab bar
			var pAttributes:Attributes = new Attributes(0, 0, pContainer.attributes.width, 
				pContainer.attributes.height);
			m_pTabBar = new TabBar(pContainer, TABBAR, pAttributes);
			m_pTabBar.addEventListener(ButtonEvent.CLICK, OnTabClick);
			
			// Append the tab bar to the XML and refresh
			pContainer.xml.appendChild(TABBAR);
			pContainer.AppendChild(m_pTabBar);
			layout(attributes);
			
			// Update the contents of the tab bar
			m_pTabBar.UpdateTabs(pTabs, sCurrentTabID);
		}

		// Load the sequence cassettes component
		protected function LoadSequenceCassettes(sContainerID:String):void
		{
			// Get the cassettes container
			var pContainer:Form = Form(findViewById(sContainerID));
			
			// Load the cassettes component
			var pAttributes:Attributes = new Attributes(0, 0, pContainer.attributes.width, 
				pContainer.attributes.height);
			m_pSequenceCassettes = new SequenceCassettes(pContainer, SEQUENCECASSETTES, pAttributes,
				m_nUnitOperationWidth, m_nButtonSkinWidth, m_pElixys);
			m_pSequenceCassettes.addEventListener(SelectionEvent.CHANGE, OnSelectionChange);
			
			// Append the sequence cassettes to the XML and refresh
			pContainer.xml.appendChild(SEQUENCECASSETTES);
			pContainer.AppendChild(m_pSequenceCassettes);
			layout(attributes);
		}
		
		// Load the sequence tools component
		protected function LoadSequenceTools(sContainerID:String):void
		{
			// Get the tools container
			var pContainer:Form = Form(findViewById(sContainerID));
			
			// Load the tools component
			var pAttributes:Attributes = new Attributes(0, 0, pContainer.attributes.width, 
				pContainer.attributes.height);
			m_pSequenceTools = new SequenceTools(pContainer, SEQUENCETOOLS, pAttributes, m_nUnitOperationWidth,
				m_nButtonSkinWidth, m_pElixys);
			
			// Append the sequence tools to the XML and refresh
			pContainer.xml.appendChild(SEQUENCETOOLS);
			pContainer.AppendChild(m_pSequenceTools);
			layout(attributes);
		}
		
		// Load the sequencer
		protected function LoadSequencer(sContainerID:String, pSequencerXML:XML):void
		{
			// Get the sequencer container
			var pContainer:Form = Form(findViewById(sContainerID));
			
			// Load the sequencer
			var pAttributes:Attributes = new Attributes(0, 0, pContainer.attributes.width, 
				pContainer.attributes.height);
			m_pSequencer = new Sequencer(pContainer, pSequencerXML, pAttributes, m_nUnitOperationWidth,
				m_nButtonSkinWidth);
			m_pSequencer.addEventListener(SelectionEvent.CHANGE, OnSelectionChange);
			m_pSequencer.addEventListener(ButtonEvent.CLICK, OnButtonClick);
			
			// Append the navigation bar to the XML and refresh
			pContainer.xml.appendChild(pSequencerXML);
			pContainer.AppendChild(m_pSequencer);
			layout(attributes);
		}

		/***
		 * Member functions
		 **/

		// Updates the state
		public override function UpdateState(pState:State):void
		{
			// Check what has changed since our last update
			var pStateSequence:StateSequence = new StateSequence(Constants.VIEW, null, pState);
			var bButtonsChanged:Boolean = true, bComponentChanged:Boolean = true;
			if (m_pStateSequence != null)
			{
				bButtonsChanged = !Elixys.JSON.State.Button.CompareButtonArrays(pStateSequence.Buttons, m_pStateSequence.Buttons);
				bComponentChanged = (pStateSequence.ClientState.ComponentID != m_pStateSequence.ClientState.ComponentID);
			}

			// Update the navigation bar buttons
			if (bButtonsChanged)
			{
				m_pNavigationBar.UpdateButtons(pStateSequence.Buttons);
			}

			// Update the cassettes and sequencer
			if (bComponentChanged)
			{
				if (m_pSequenceCassettes != null)
				{
					m_pSequenceCassettes.UpdateSelectedComponent(pStateSequence.ClientState.ComponentID);
				}
				m_pSequencer.UpdateSelectedComponent(pStateSequence.ClientState.ComponentID);
			}

			// Update the tools
			if (m_pSequenceTools != null)
			{
				m_pSequenceTools.Update();
			}

			// Remember the new state
			m_pStateSequence = pStateSequence;
			
			// Fetch the sequence and component from the server
			DoGet("/Elixys/sequence/" + pState.ClientState.SequenceID);
			DoGet("/Elixys/sequence/" + pState.ClientState.SequenceID + "/component/" + pState.ClientState.ComponentID);
		}

		// Updates the sequence
		public override function UpdateSequence(pSequence:Sequence):void
		{
			// Check if the sequence has changed
			var bSequenceChanged:Boolean = true;
			if (m_pSequence != null)
			{
				bSequenceChanged = !Sequence.CompareSequences(pSequence, m_pSequence);
			}

			// Update the cassettes and sequencer
			if (bSequenceChanged)
			{
				if (m_pSequenceCassettes != null)
				{
					m_pSequenceCassettes.UpdateSequence(pSequence);
				}
				for (var nIndex:int = 0; nIndex < m_pSubviews.length; ++nIndex)
				{
					(m_pSubviews[nIndex] as SubviewBase).UpdateSequence(pSequence);
				}
				m_pSequencer.UpdateSequence(pSequence);
			}
			
			// Update the title label
			if (m_pTitleLabel != null)
			{
				m_pTitleLabel.width = m_pTitleBackground.width;
				m_pTitleLabel.text = pSequence.Metadata.Name.toUpperCase();
				m_pTitleLabel.x = m_pTitleBackground.x + TITLE_TEXT_OFFSET;
				m_pTitleLabel.y = (m_pTitle.attributes.height - m_pTitleLabel.height) / 2;
			}
			
			// Remember the new sequence
			m_pSequence = pSequence;
		}
		
		// Updates the component
		public override function UpdateComponent(pComponent:ComponentBase):void
		{
			// Check if the component has changed
			var bComponentChanged:Boolean = true;
			if (m_pComponent != null)
			{
				bComponentChanged = !ComponentBase.CompareComponents(pComponent, m_pComponent);
			}

			// Update the cassettes
			if (bComponentChanged && (m_pSequenceCassettes != null))
			{
				m_pSequenceCassettes.UpdateComponent(pComponent);
			}

			// Update and show the appropriate subview
			if (bComponentChanged)
			{
				var nIndex:int, pSubview:SubviewBase;
				for (nIndex = 0; nIndex < m_pSubviews.length; ++nIndex)
				{
					pSubview = m_pSubviews[nIndex] as SubviewBase;
					if (pSubview.SubviewType == pComponent.ComponentType)
					{
						pSubview.UpdateComponent(pComponent);
						pSubview.visible = true;
					}
					else
					{
						pSubview.visible = false;
					}
				}
			}
			
			// Remember the new component
			m_pComponent = pComponent;
		}

		// Called when a button on the navigation bar is clicked
		protected function OnButtonClick(event:ButtonEvent):void
		{
			// Send a button click to the server
			var pPostSequence:PostSequence = new PostSequence();
			pPostSequence.TargetID = event.button;
			DoPost(pPostSequence, m_sMode);
		}

		// Called when a tab on the tab bar is clicked
		protected function OnTabClick(event:ButtonEvent):void
		{
			// Handle in derived classes
		}

		// Called when the unit operation selection changes
		protected function OnSelectionChange(event:SelectionEvent):void
		{
			// Send the unit operation click to the server
			var pPostSequence:PostSequence = new PostSequence();
			pPostSequence.TargetID = event.selectionID.toString();
			DoPost(pPostSequence, m_sMode);
		}

		/***
		 * Member variables
		 **/
		
		// Title XML
		protected static const TITLE:XML =
			<frame>
				<label id="titlelabel" useEmbedded="true">
					<font face="GothamBold" color={Styling.TEXT_WHITE} size="18"/>
				</label>
			</frame>;

		// Tab bar XML
		protected static const TABBAR:XML =
			<tab alignH="fill" alignV="fill" fontFace="GothamMedium" fontSize="14" textColor={Styling.TEXT_GRAY4}
				selectedTextColor={Styling.TEXT_GRAY1} textpaddingvertical="7" tabpercentwidth="50" />;

		// Cassettes XML
		protected static const SEQUENCECASSETTES:XML =
			<sequencecassette alignH="fill" alignV="fill" fontface="GothamBold" fontsize="34" 
				enabledtextcolor={Styling.TEXT_GRAY2} activetextcolor={Styling.TEXT_BLUE1}
				pressedtextcolor={Styling.TEXT_WHITE} quickviewfontface="GothamBold" 
				quickviewfontsize="16" quickviewcolor={Styling.TEXT_BLACK} />;

		// Tools XML
		protected static const SEQUENCETOOLS:XML =
			<sequencetools alignH="fill" alignV="fill" fontface="GothamBold" fontsize="8" 
				enabledtextcolor={Styling.TEXT_GRAY2} pressedtextcolor={Styling.TEXT_WHITE} />;
		
		// Subviews
		protected static var m_pSubviewTypes:Array = [SubviewCassette, SubviewReact, SubviewAdd, SubviewEvaporate,
			SubviewTransfer, SubviewPrompt, SubviewInstall, SubviewComment, SubviewTrapF18, SubviewEluteF18,
			SubviewInitialize, SubviewMix, SubviewMove, SubviewExternalAdd];
		protected var m_pSubviews:Array = new Array();
		protected var m_pSubviewContainer:Form;

		// Number of steps required to load the sequence base components
		public static var BASE_LOAD_STEPS:uint = m_pSubviewTypes.length;

		// The current step
		protected var m_nChildrenLoaded:uint = 0;

		// Mode
		protected var m_sMode:String = "";
		
		// Currently displayed state, sequence and component
		protected var m_pStateSequence:StateSequence;
		protected var m_pSequence:Sequence;
		protected var m_pComponent:ComponentBase;
		
		// Screen components
		protected var m_pNavigationBar:NavigationBar;
		protected var m_pTitle:Form;
		protected var m_pTitleLabel:UILabel;
		protected var m_pTitleBackground:MovieClip;
		protected var m_pTabBar:TabBar;
		protected var m_pSequenceCassettes:SequenceCassettes;
		protected var m_pSequenceTools:SequenceTools;
		protected var m_pSequencer:Sequencer;
		
		// Unit operation and button widths
		protected var m_nUnitOperationWidth:Number = 0;
		protected var m_nButtonSkinWidth:Number = 0

		// Constants
		protected static var TITLE_TEXT_OFFSET:int = 8;
		protected static var TITLE_PADDING:int = 20;
	}
}
