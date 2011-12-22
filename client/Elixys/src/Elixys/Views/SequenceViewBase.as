package Elixys.Views
{
	import Elixys.Events.HTTPRequestEvent;
	import Elixys.HTTP.HTTPConnection;
	import Elixys.HTTP.HTTPRequest;
	import Elixys.Objects.*;
	
	import flash.display.DisplayObject;
	import flash.display.DisplayObjectContainer;
	import flash.events.EventDispatcher;
	import flash.events.MouseEvent;
	import flash.utils.ByteArray;
	
	import mx.collections.ArrayList;
	import mx.containers.ViewStack;
	import mx.events.FlexEvent;
	
	import spark.components.Button;
	import spark.components.HGroup;
	import spark.components.Label;
	import spark.components.List;
	import spark.components.VGroup;

	public class SequenceViewBase extends ViewBase
	{
		/**
		 * Member functions
		 **/

		// Constructor
		public function SequenceViewBase()
		{
			// Call the base constructor
			super();
		}

		// Return the state, sequence and component IDs
		public function GetStateSequence():StateSequence
		{
			return m_pStateSequence;
		}
		public function GetSequenceID():uint
		{
			return m_nSequenceID;
		}
		public function GetComponentID():uint
		{
			return m_nComponentID;
		}
		
		// Returns the active reactor from the server state
		public function GetReactor(nReactor:uint):ReactorState
		{
			// Locate the reactor
			if (m_pStateSequence != null)
			{
				var pServeState:ServerState = m_pStateSequence.ServerState();
				var pReactors:Array = pServeState.HardwareState().Reactors();
				for (var nReactor:uint = 0; nReactor < pReactors.length; ++nReactor)
				{
					var pReactor:ReactorState = pReactors[nReactor] as ReactorState;
					if (pReactor.ReactorNumber() == nReactor)
					{
						// Found it
						return pReactor;
					}
				}
			}
			
			// Reactor not found
			return null;
		}

		// Update server configuration
		public override function UpdateConfiguration(pConfiguration:Configuration):void
		{
			// Remember the server configuration
			m_pServerConfiguration = pConfiguration;

			// Fill the unit operations list if the derived view supports it
			if (m_pUnitOperationsList)
			{
				UpdateUnitOperationsList(m_pUnitOperationsList, pConfiguration.SupportedOperations());
			}
		}
		
		// Update the sequence state
		protected function UpdateSequenceState(pState:State, sStateType:String):void
		{
			// Update our button array with the server data
			var pStateSequence:StateSequence = new StateSequence(sStateType, null, pState);
			if (m_pNavigationButtons != null)
			{
				UpdateButtons(m_pNavigationButtons, pStateSequence.NavigationButtons(), CreateNewButton);
				function CreateNewButton():spark.components.Button
				{
					// Callback to create our new button
					var pButton:spark.components.Button = new spark.components.Button();
					pButton.width = 150;
					pButton.height = 40;
					pButton.styleName = "button";
					pButton.addEventListener(MouseEvent.CLICK, m_pOnButtonClick);
					return pButton;
				}
			}
			
			// Remember the state, sequence and component
			m_pStateSequence = pStateSequence;
			m_nSequenceID = pStateSequence.ClientState().SequenceID();
			m_nComponentID = pStateSequence.ClientState().ComponentID();

			// Update the subview component
			var pSubview:SubviewBase = m_pElixysMain.GetActiveSubview();
			if (pSubview != null)
			{
				pSubview.UpdateState(pState);
			}

			// Request the sequence from the server
			RequestSequence(m_nSequenceID);
		}
		
		// Update the sequence sequence
		public function UpdateSequenceSequence(pSequence:Sequence):void
		{
			// Set the sequence name
			m_pSequenceName.text = pSequence.Metadata().Name;
			
			// Fill the operations list
			UpdateSequenceComponentList(m_pSequenceList, pSequence.Components(), m_nComponentID);
			
			// Update all of the items in the sequence list
			var pArrayList:ArrayList = m_pSequenceList.dataProvider as ArrayList;
			for (var i:uint = 0; i < pArrayList.length; ++i)
			{
				var pComponent:SequenceComponent = pArrayList.getItemAt(i) as SequenceComponent;
				pArrayList.itemUpdated(pArrayList.getItemAt(i));
			}
		}
		
		// Update the sequence component
		public function UpdateSequenceComponent(pComponent:Component):void
		{
			// Make sure the subview is visible
			m_pElixysMain.ShowSubview(pComponent.ComponentType, m_sViewMode, m_pComponentGroup);
			
			// Update the subview component
			var pSubview:SubviewBase = m_pElixysMain.GetActiveSubview();
			if (pSubview != null)
			{
				pSubview.UpdateComponent(pComponent);
			}
		}
		
		// Update sequence reagent
		public function UpdateSequenceReagents(pReagents:Array):void
		{
			// Update the subview component
			var pSubview:SubviewBase = m_pElixysMain.GetActiveSubview();
			if (pSubview != null)
			{
				pSubview.UpdateReagents(pReagents);
			}
		}
		
		// Send requests to the server
		public function DoGet(sURL:String):void
		{
			// Pass the request up to be sent to the server
			var pHTTPRequest:HTTPRequest = new HTTPRequest();
			pHTTPRequest.m_sMethod = "GET";
			pHTTPRequest.m_sResource = "/Elixys/" + sURL;
			dispatchEvent(new HTTPRequestEvent(pHTTPRequest));
		}
		public function DoPost(pPost:Object, sViewName:String):void
		{
			// Convert the request to a byte array
			var pBody:ByteArray = new ByteArray();
			if (pPost != null)
			{
				pBody.writeMultiByte(pPost.toString(), "utf8");
				pBody.position = 0;
			}
			
			// Pass the request up to be sent to the server
			var pHTTPRequest:HTTPRequest = new HTTPRequest();
			pHTTPRequest.m_sMethod = "POST";
			pHTTPRequest.m_sResource = "/Elixys/" + sViewName;
			pHTTPRequest.m_pBody = pBody;
			dispatchEvent(new HTTPRequestEvent(pHTTPRequest));
		}
		public function DoDelete(sURL:String):void
		{
			// Pass the request up to be sent to the server
			var pHTTPRequest:HTTPRequest = new HTTPRequest();
			pHTTPRequest.m_sMethod = "DELETE";
			pHTTPRequest.m_sResource = "/Elixys/" + sURL;
			dispatchEvent(new HTTPRequestEvent(pHTTPRequest));
		}
		
		// Walk the decendant tree until we find a child with the given name
		protected function FindDecendentByName(pTarget:DisplayObjectContainer, sName:String):DisplayObject
		{
			// Make sure our target is valid
			if (pTarget == null)
			{
				return null;
			}
			
			// Check if our target is the one we are searching for
			if (pTarget.name == sName)
			{
				return pTarget;
			}
			
			// Walk the immediate children
			for (var nChild:uint = 0; nChild < pTarget.numChildren; ++nChild)
			{
				var pChild:DisplayObject = pTarget.getChildAt(nChild);
				if (pChild.name == sName)
				{
					return pChild;
				}
				else
				{
					// Call this function recursively for all children
					pChild = FindDecendentByName(pChild as DisplayObjectContainer, sName);
					if (pChild != null)
					{
						return pChild;
					}
				}
			}
			return null;
		}

		// Inserts the unit operation
		protected function InsertUnitOperation(sUnitOperation:String, nInsertionTarget:int):void
		{
			// Create a blank instance of the appropriate unit operation
			var pComponent:Component;
			switch (sUnitOperation.toUpperCase())
			{
				case ComponentAdd.TYPE:
					pComponent = new ComponentAdd();
					break;
				
				case ComponentComment.TYPE:
					pComponent = new ComponentComment();
					break;
				
				case ComponentEvaporate.TYPE:
					pComponent = new ComponentEvaporate();
					break;
				
				case ComponentInstall.TYPE:
					pComponent = new ComponentInstall();
					break;
				
				case ComponentPrompt.TYPE:
					pComponent = new ComponentPrompt();
					break;
				
				case ComponentReact.TYPE:
					pComponent = new ComponentReact();
					break;
				
				case ComponentTransfer.TYPE:
					pComponent = new ComponentTransfer();
					break;
				
				case ComponentInitialize.TYPE:
					pComponent = new ComponentInitialize();
					break;
				
				case ComponentTrapF18.TYPE:
					pComponent = new ComponentTrapF18();
					break;
				
				case ComponentEluteF18.TYPE:
					pComponent = new ComponentEluteF18();
					break;
				
				case ComponentMix.TYPE:
					pComponent = new ComponentMix();
					break;
				
				case ComponentMove.TYPE:
					pComponent = new ComponentMove();
					break;
				
				default:
					throw Error("Unknown component type: " + sUnitOperation);
			}
			
			// Post the new component to the server
			var sURL:String = "sequence/" + m_nSequenceID + "/component/0"
			if (nInsertionTarget != -1)
			{
				sURL += "/" + nInsertionTarget;
			}
			DoPost(pComponent, sURL);
		}

		// Button click handler
		public function OnButtonClick(event:MouseEvent):void
		{
		}
		
		/***
		 * Member variables
		 **/
		
		// State, sequence and component IDs
		protected var m_pStateSequence:StateSequence = null;
		protected var m_nSequenceID:uint = 0;
		protected var m_nComponentID:uint = 0;

		// Current view mode
		protected var m_sViewMode:String;

		// Server configuration
		protected var m_pServerConfiguration:Configuration = null;
		
		// Pointer to the button click handler of the derived class
		protected var m_pOnButtonClick:Function = null;

		// Pointers to the UI component of the derived class
		protected var m_pUnitOperationsList:List = null;
		protected var m_pSequenceName:Label = null;
		protected var m_pSequenceList:List = null;
		protected var m_pNavigationButtons:HGroup = null;
		protected var m_pComponentGroup:VGroup = null;
	}
}
