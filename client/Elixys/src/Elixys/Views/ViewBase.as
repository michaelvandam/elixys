package Elixys.Views
{
	import Elixys.Events.ChildCreationCompleteEvent;
	import Elixys.Events.HTTPRequestEvent;
	import Elixys.HTTP.HTTPRequest;
	import Elixys.Objects.*;
	import Elixys.Validation.*;
	
	import flash.display.DisplayObject;
	import flash.display.DisplayObjectContainer;
	import flash.events.EventDispatcher;
	import flash.events.FocusEvent;
	
	import mx.collections.ArrayList;
	import mx.collections.IList;
	import mx.containers.Canvas;
	import mx.containers.TabNavigator;
	import mx.controls.Button;
	import mx.controls.TextArea;
	import mx.core.UIComponent;
	import mx.events.FlexEvent;
	
	import spark.components.ComboBox;
	import spark.components.DataGrid;
	import spark.components.Group;
	import spark.components.List;
	import spark.components.TextInput;
	import spark.components.VGroup;
	import spark.components.gridClasses.GridColumn;
	import spark.components.supportClasses.SkinnableTextBase;
	
	public class ViewBase extends Canvas
	{
		/***
		 * Member functions
		 **/
		
		// Constructor
		public function ViewBase()
		{
			// Call the base constructor
			super();

			// Add event listeners
			addEventListener(FlexEvent.CREATION_COMPLETE, OnCreationComplete);
		}
		
		// Called when creation is complete
		protected function OnCreationComplete(event:FlexEvent):void
		{
			// Inform the main window that we are up and running
			dispatchEvent(new ChildCreationCompleteEvent());
		}

		// Sets the main Elixys window
		public function SetElixysMain(pElixysMain:ElixysMain):void
		{
			m_pElixysMain = pElixysMain;
		}

		// Functions that are overridden by derived classes
		public function UpdateConfiguration(pConfiguration:Configuration):void
		{
		}
		public function UpdateState(pState:State):void
		{
		}
		public function UpdateSequence(pSequence:Sequence):void
		{
		}
		public function UpdateComponent(pComponent:Component):void
		{
		}
		public function UpdateReagents(pReagents:Array):void
		{
		}
		protected function OnTextValueChanged(pFocusTarget:TextArea):void
		{
		}
		
		// Request a sequence from the server
		protected function RequestSequence(nSequenceID:uint):void
		{
			// Create and send an HTTP request to the server
			var pHTTPRequest:HTTPRequest = new HTTPRequest();
			pHTTPRequest.m_sMethod = "GET";
			pHTTPRequest.m_sResource = "/Elixys/sequence/" + nSequenceID;
			dispatchEvent(new HTTPRequestEvent(pHTTPRequest));
		}
		
		// Request a sequence component from the server
		protected function RequestSequenceComponent(nSequenceID:uint, nComponentID:uint):void
		{
			// Create and send an HTTP request to the server
			var pHTTPRequest:HTTPRequest = new HTTPRequest();
			pHTTPRequest.m_sMethod = "GET";
			pHTTPRequest.m_sResource = "/Elixys/sequence/" + nSequenceID + "/component/" + nComponentID;
			dispatchEvent(new HTTPRequestEvent(pHTTPRequest));
		}
		
		// Request the sequence reagent from the server
		protected function RequestSequenceReagents(pReagentIDs:Array, nSequenceID:uint = 0):void
		{
			// Look up our sequence ID if one was not provided
			if (!nSequenceID)
			{
				nSequenceID = m_pElixysMain.GetActiveSequenceView().GetSequenceID();
			}

			// Format the reagent IDs
			var sReagentIDs:String = "";
			for (var i:uint = 0; i < pReagentIDs.length; ++i)
			{
				if (pReagentIDs[i] == 0)
				{
					continue;
				}
				if (i != 0)
				{
					sReagentIDs += ".";					
				}
				sReagentIDs += pReagentIDs[i];
			}
			
			// Return if we have no reagents to get
			if (sReagentIDs == "")
			{
				return;
			}

			// Create and send a GET request to the server
			var pHTTPRequest:HTTPRequest = new HTTPRequest();
			pHTTPRequest.m_sMethod = "GET";
			pHTTPRequest.m_sResource = "/Elixys/sequence/" + nSequenceID + "/reagent/" + sReagentIDs;
			m_pElixysMain.GetActiveSequenceView().dispatchEvent(new HTTPRequestEvent(pHTTPRequest));
		}
		
		// Called when a text control receives focus
		public function OnTextFocusIn(event:FocusEvent):void
		{
			// Remember the text area object that has the keyboard focus
			var pParent:DisplayObject = event.target as DisplayObject;
			while ((pParent != null) && ((pParent as TextArea) == null))
			{
				pParent = pParent.parent;
			}
			if (pParent == null)
			{
				throw Error("Failed to locate TextArea");
			}
			m_pKeyboardFocusTextArea = pParent as TextArea;
			
			// Remember the initial text
			m_sKeyboardFocusInitialText = m_pKeyboardFocusTextArea.text;
		}
		
		// Called when a text control loses focus
		public function OnTextFocusOut(event:FocusEvent):void
		{
			if (m_pKeyboardFocusTextArea != null)
			{
				// Has the value of the text input changed?
				if (m_pKeyboardFocusTextArea.text != m_sKeyboardFocusInitialText)
				{
					// Yes, so update and save the component
					OnTextValueChanged(m_pKeyboardFocusTextArea);
				}
				
				// Clear our pointer
				m_pKeyboardFocusTextArea = null;
			}
		}
		
		// Returns the item that currently has the keyboard focus
		public function KeyboardFocusTextArea():TextArea
		{
			return m_pKeyboardFocusTextArea;
		}

		// Update the client button array with the server array
		protected function UpdateButtons(pClientButtons:Group, pServerButtons:Array, fCreateNewButton:Function):void
		{
			// Loop through the server and client button arrays
			var nButton:uint, pButtonClient:spark.components.Button, pButtonServer:Elixys.Objects.Button;
			for (nButton = 0; nButton < pServerButtons.length; ++nButton)
			{
				// Either get a pointer to the existing button or create a new one
				if (nButton < pClientButtons.numElements)
				{
					// Use the existing button
					pButtonClient = pClientButtons.getElementAt(nButton) as spark.components.Button;
				}
				else
				{
					// Create a new button
					pButtonClient = fCreateNewButton();
					pClientButtons.addElement(pButtonClient);
				}
			
				// Update the button text and ID
				pButtonServer = pServerButtons[nButton];
				pButtonClient.label = pButtonServer.Text();
				pButtonClient.id = pButtonServer.ID();
			}
		
			// Remove any extra buttons
			while (nButton < pClientButtons.numElements)
			{
				pClientButtons.removeElementAt(pClientButtons.numElements - 1);
			}
		}

		// Update the client tab array with the server array
		protected function UpdateTabs(pTabNavigator:TabNavigator, pServerTabs:Array, fCreateNewTab:Function, sCurrentTabID:String):void
		{
			// Loop through the server and client tab arrays
			var nTab:uint, pTabClient:SelectSubview, pTabServer:Elixys.Objects.Tab;
			for (nTab = 0; nTab < pServerTabs.length; ++nTab)
			{
				// Either get a pointer to the existing tab or create a new one
				if (nTab < pTabNavigator.numChildren)
				{
					// Use the existing button
					pTabClient = pTabNavigator.getChildAt(nTab) as SelectSubview;
				}
				else
				{
					// Create a new tab
					pTabClient = fCreateNewTab();
					pTabNavigator.addChild(pTabClient);
				}
			
				// Update the tab label and ID
				pTabServer = pServerTabs[nTab];
				pTabClient.label = pTabServer.Text();
				pTabClient.id = pTabServer.ID();

				// Update the tab columns
				UpdateColumns(pTabClient._sequenceGrid.columns, pTabServer.Columns());
				
				// Select the current tab
				if (pTabClient.id == sCurrentTabID)
				{
					pTabNavigator.selectedChild = pTabClient;
				}
			}
		
			// Remove any extra tabs
			while (nTab < pTabNavigator.numChildren)
			{
				pTabNavigator.removeChildAt(pTabNavigator.numChildren - 1);
			}
		}
		
		// Update the client data grid columns with the server data
		protected function UpdateColumns(pColumnsClient:IList, pColumnsServer:Array):void
		{
			// Loop through the server and client data grid columns
			var nColumn:uint, pColumnClient:GridColumn, pHeadersServer:Array;
			for (nColumn = 0; nColumn < pColumnsServer.length; ++nColumn)
			{
				// Either get a pointer to the existing column or create a new one
				if (nColumn < pColumnsClient.length)
				{
					// Use the existing button
					pColumnClient = pColumnsClient.getItemAt(nColumn) as GridColumn;
				}
				else
				{
					// Create a new tab
					pColumnClient = new GridColumn();
					pColumnsClient.addItem(pColumnClient);
				}
				
				// Update the data field and header
				pHeadersServer = pColumnsServer[nColumn].split(":");
				pColumnClient.dataField = pHeadersServer[0];
				pColumnClient.headerText = pHeadersServer[1];
			}
			
			// Remove any extra tabs
			while (nColumn < pColumnsClient.length)
			{
				pColumnsClient.removeItemAt(pColumnsClient.length - 1);
			}
		}

		// Update the client sequence grid with the server data
		protected function UpdateDataGrid(pDataGrid:DataGrid, pServerSequences:Array, fCreateNewSequence:Function):void
		{
			// Get a pointer to the sequence grid
			var pGridData:ArrayList;
			if (pDataGrid.dataProvider != null)
			{
				pGridData = pDataGrid.dataProvider as ArrayList;
			}
			if (pGridData == null)
			{
				pGridData = new ArrayList();
			}
		
			// Get the ID of the currently selected sequence
			var pSelectedID:String = "";
			if (pDataGrid.selectedItem)
			{
				pSelectedID = (pDataGrid.selectedItem as SequenceMetadata).ID;
			}

			// Loop through the server and client sequence arrays
			var nSequence:uint, pClientSequence:SequenceMetadata, pServerSequence:SequenceMetadata;
			for (nSequence = 0; nSequence < pServerSequences.length; ++nSequence)
			{
				// Either get a pointer to the existing sequence or create a new one
				if (nSequence < pGridData.length)
				{
					// Use the existing sequence
					pClientSequence = pGridData.getItemAt(nSequence) as SequenceMetadata;
				}
				else
				{
					// Create a new sequence
					pClientSequence = fCreateNewSequence();
					pGridData.addItem(pClientSequence);
				}
				
				// Update the sequence metadata
				pClientSequence.Copy(pServerSequences[nSequence]);
				
				// Make sure the currently selected sequence is reselected
				if (pClientSequence.ID == pSelectedID)
				{
					pDataGrid.selectedItem = pClientSequence;
				}
			}
		
			// Remove any extra sequences
			while (nSequence < pGridData.length)
			{
				pGridData.removeItemAt(pGridData.length - 1);
			}
			
			// Update the data provider
			pDataGrid.dataProvider = pGridData;
		}
		
		// Update the client sequence component array with the server values
		protected function UpdateSequenceComponentList(pList:List, pServerComponents:Array, nCurrentComponentID:uint):void
		{
			// Get a pointer to the sequence data provider
			var pListData:ArrayList;
			if (pList.dataProvider != null)
			{
				pListData = pList.dataProvider as ArrayList;
			}
			if (pListData == null)
			{
				pListData = new ArrayList();
			}

			// Loop through the server and client component arrays
			var nComponent:uint, pComponentClient:SequenceComponent, pComponentServer:SequenceComponent, nNonCassetteCount:uint = 1;
			for (nComponent = 0; nComponent < pServerComponents.length; ++nComponent)
			{
				// Either get a pointer to the existing component or create a new one
				if (nComponent < pListData.length)
				{
					// Use the existing component
					pComponentClient = pListData.getItemAt(nComponent) as SequenceComponent;
				}
				else
				{
					// Create a new component
					pComponentClient = new SequenceComponent();
					pListData.addItem(pComponentClient);
				}
				
				// Reset the selected index
				pList.selectedIndex = -1;

				// Update the sequence component
				pComponentClient.Copy(pServerComponents[nComponent]);
				if (pComponentClient.ComponentType == ComponentCassette.TYPE)
				{
					pComponentClient.DisplayIndex = 0;
				}
				else
				{
					pComponentClient.DisplayIndex = nNonCassetteCount++;
				}
				
				// Make sure the currently selected sequence is reselected
				if (pComponentClient.ID == nCurrentComponentID)
				{
					pList.selectedItem = pComponentClient;
				}
			}
			
			// Remove any extra sequences
			while (nComponent < pListData.length)
			{
				pListData.removeItemAt(pListData.length - 1);
			}
			
			// Update the data provider
			pList.dataProvider = pListData;
		}

		// Update the client unit operations array with the server values
		protected function UpdateUnitOperationsList(pList:List, pUnitOperations:Array):void
		{
			// Create a new data provider
			var pListData:ArrayList = new ArrayList();
			
			// Loop through the server unit operations
			for each (var sUnitOperation:String in pUnitOperations)
			{
				pListData.addItem(sUnitOperation);
			}
			
			// Update the data provider
			pList.dataProvider = pListData;
		}
		
		// Update the client reagent grid with the server data
		protected function UpdateReagentGrid(pGrid:DataGrid, pServerReagents:Array):void
		{
			// Get a pointer to the sequence grid
			var pGridData:ArrayList;
			if (pGrid.dataProvider != null)
			{
				pGridData = pGrid.dataProvider as ArrayList;
			}
			if (pGridData == null)
			{
				pGridData = new ArrayList();
			}
			
			// Make sure we have enough reagent positions in our array
			var nReagent:uint, pReagent:Reagent;
			for (nReagent = 0; nReagent < pServerReagents.length; ++nReagent)
			{
				// Get a pointer to the next reagent
				if (nReagent < pGridData.length)
				{
					// Use existing reagent
					pReagent = pGridData.getItemAt(nReagent) as Reagent;
				}
				else
				{
					// Create a new reagent
					pReagent = new Reagent();
					pGridData.addItem(pReagent);
				}
				
				// Update the reagent
				pReagent.Copy(pServerReagents[nReagent]);
				pGridData.setItemAt(pReagent, nReagent);
			}
			
			// Remove any extra reagents
			while (nReagent < pGridData.length)
			{
				pGridData.removeItemAt(pGridData.length - 1);
			}
			
			// Update the data provider
			pGrid.dataProvider = pGridData;
		}

		// Update the given combo box with the specified enum-number validation string
		protected function UpdateEnumNumberComboBox(sEnumNumberValidation:String, pComboBox:ComboBox, sCurrentValue:String):void
		{
			// Get a pointer to the data provider
			var pData:ArrayList;
			if (pComboBox.dataProvider != null)
			{
				pData = pComboBox.dataProvider as ArrayList;
			}
			if (pData == null)
			{
				pData = new ArrayList();
			}
			
			// Reset the selected index
			pComboBox.selectedIndex = -1;
		
			// Make sure we have a validation string
			var nValue:uint = 0;
			if (sEnumNumberValidation != null)
			{
				// Get the array of number values
				var pEnumNumberValidation:EnumNumberValidation = new EnumNumberValidation(sEnumNumberValidation);
				var pNumberValues:Array = pEnumNumberValidation.NumberValues();
	
				// Loop through the server and client arrays
				while (nValue < pNumberValues.length)
				{
					// Either set the existing item or create a new one
					if (nValue < pData.length)
					{
						// Update the existing item
						pData.setItemAt(pNumberValues[nValue], nValue);
					}
					else
					{
						// Create a new item
						pData.addItem(pNumberValues[nValue]);
					}
					
					// Make sure the currently selected value is reselected
					if (pData.getItemAt(nValue) == sCurrentValue)
					{
						pComboBox.selectedIndex = nValue;
					}
					
					// Increment our counter
					++nValue;
				}
			}			
			// Remove any extra values
			while (nValue < pData.length)
			{
				pData.removeItemAt(pData.length - 1);
			}
			
			// Update the data provider
			pComboBox.dataProvider = pData;
		}
		
		// Update the given combo box with the specified enum-reagent validation string
		protected function UpdateEnumReagentComboBox(sEnumReagentValidation:String, pComboBox:ComboBox, pCurrentReagent:Reagent):void
		{
			// Get the array of reagent IDs if we have a validation string
			var pReagentIDs:Array = null;
			if (sEnumReagentValidation != null)
			{
				var pEnumReagentValidation:EnumReagentValidation = new EnumReagentValidation(sEnumReagentValidation);
				pReagentIDs = pEnumReagentValidation.ReagentIDs();
			}
			
			// Call the shared implementation
			UpdateEnumComboBox(pReagentIDs, pComboBox, pCurrentReagent.ReagentID);
		}

		// Update the given combo box with the specified enum-target validation string
		protected function UpdateEnumTargetComboBox(sEnumTargetValidation:String, pComboBox:ComboBox, pCurrentTarget:Reagent):void
		{
			// Get the array of target IDs if we have a validation string
			var pTargetIDs:Array = null;
			if (sEnumTargetValidation != null)
			{
				var pEnumTargetValidation:EnumTargetValidation = new EnumTargetValidation(sEnumTargetValidation);
				pTargetIDs = pEnumTargetValidation.TargetIDs();
			}
			
			// Call the shared implementation
			UpdateEnumComboBox(pTargetIDs, pComboBox, pCurrentTarget.ReagentID);
		}

		// Shared combo box update function
		private function UpdateEnumComboBox(pIDs:Array, pComboBox:ComboBox, nCurrentReagentID:uint):void
		{
			// Get a pointer to the data provider
			var pData:ArrayList;
			if (pComboBox.dataProvider != null)
			{
				pData = pComboBox.dataProvider as ArrayList;
			}
			if (pData == null)
			{
				pData = new ArrayList();
			}
			
			// Reset the selected index
			pComboBox.selectedIndex = -1;

			// Loop through the server and client arrays
			var nReagent:uint = 0;
			var pReagentIDs:Array = new Array();
			if (pIDs != null)
			{
				var pReagentClient:Reagent;
				for (nReagent = 0; nReagent < pIDs.length; ++nReagent)
				{
					// Get a pointer to an existing reagent or create a new one
					if (nReagent < pData.length)
					{
						// Use the existing reagent
						pReagentClient = pData.getItemAt(nReagent) as Reagent;
					}
					else
					{
						// Create a new reagent
						pReagentClient = new Reagent();
						pData.addItem(pReagentClient);
					}
					
					// Update the reagent ID
					pReagentClient.ReagentID = pIDs[nReagent];
					pReagentIDs.push(pReagentClient.ReagentID);
	
					// Make sure the currently selected reagent is reselected
					if (pReagentClient.ReagentID == nCurrentReagentID)
					{
						pComboBox.selectedIndex = nReagent;
					}
				}
			}
			
			// Remove any extra values
			while (nReagent < pData.length)
			{
				pData.removeItemAt(pData.length - 1);
			}
			
			// Update the data provider
			pComboBox.dataProvider = pData;

			// Request the reagents from the server
			RequestSequenceReagents(pReagentIDs);
		}
		
		// Update the reagent item in the given combo box
		protected function UpdateEnumReagentComboBoxItems(pReagents:Array, pComboBox:ComboBox):void
		{
			// Loop through each reagent we got from the server
			var nServerReagent:uint, nClientReagent:uint, pClientReagent:Reagent, pServerReagent:Reagent;
			var pData:ArrayList = pComboBox.dataProvider as ArrayList;
			for (nServerReagent = 0; nServerReagent < pReagents.length; ++nServerReagent)
			{
				// Look up the reagent in the combo box data
				pServerReagent = pReagents[nServerReagent];
				for (nClientReagent = 0; nClientReagent < pData.length; ++nClientReagent)
				{
					pClientReagent = pData.getItemAt(nClientReagent) as Reagent;
					if (pClientReagent.ReagentID == pServerReagent.ReagentID)
					{
						// Found it.  Update and break out of the inner loop
						pClientReagent.Copy(pServerReagent);
						nClientReagent = pData.length;
					}
				}
			}
		}
		
		/***
		 * Member variables
		 **/
		
		// Main Elixys window
		protected var m_pElixysMain:ElixysMain = null;

		// Keyboard focus
		protected var m_pKeyboardFocusTextArea:TextArea = null;
		private var m_sKeyboardFocusInitialText:String = "";
	}
}
